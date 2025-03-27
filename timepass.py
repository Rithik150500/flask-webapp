from flask import Flask, request, Response, jsonify, render_template
from neo4j import GraphDatabase
from openai import OpenAI
import anthropic
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import threading
import uuid
import json
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import xml.etree.ElementTree as ET
import tiktoken


app = Flask(__name__)


# ========== CONFIGURATION & INITIALIZATION ==========

# Load configuration from environment variables
NEO4J_URI = 'neo4j+s://3e0a4374.databases.neo4j.io'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = '9gqv6s7Ipk0duq1mpzSlbyoaQkLWK860HaPRKbXp7X4'

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# 
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


jobs = {}


@app.route('/cocounsel')
def cocounsel():
    return render_template('timepass.html')



@app.route('/process_dispute_sse', methods=['POST'])
def process_dispute_sse():
    print(NEO4J_URI)
    print(NEO4J_PASSWORD)

    print(ANTHROPIC_API_KEY)
    print(OPENAI_API_KEY)
    print(GEMINI_API_KEY)

    data = request.get_json()
    legal_problem = data.get('dispute', '').strip()
    if not legal_problem:
        # Return a simple SSE event with an error message and then close
        def error_stream():
            yield "event: error\ndata: No factual dispute provided\n\n"
        return Response(error_stream(), mimetype='text/event-stream')


    def sse_generator(legal_problem):
        try:

            # Step 1: Stream initial memo
            initial_memo_box = {"text": ""}
            # 1. Step: Stream the initial memo from Anthropic
            yield from stream_initial_memo(initial_memo_box, legal_problem)
            memo_text = initial_memo_box["text"]

            # ========== PARALLELIZE TASKS A & B ==========
            case_refs = parse_initial_memo(memo_text)
            main_doc_ids = query_full_text_index(case_refs)
            all_docs = get_related_docs(main_doc_ids)
                

            memo_embed = get_embed(memo_text)
            some_docs = query_vector_index(memo_embed)
            

            # with ThreadPoolExecutor(max_workers=2) as executor:
            #     futureA = executor.submit(task_A, memo_text)
            #     futureB = executor.submit(task_B, memo_text)

            #     # We'll store the results of each future
            #     case_refs, main_doc_ids, all_docs = None, None, None
            #     memo_embed, some_docs = None, None

            #     # Wait for both tasks to complete
            #     done_set = as_completed([futureA, futureB])
            #     for fut in done_set:
            #         if fut == futureA:
            #             # Unpack the results from Task A
            #             case_refs, main_doc_ids, all_docs = fut.result()
            #         else:
            #             # Unpack the results from Task B
            #             memo_embed, some_docs = fut.result()

            # 3. Next steps
            print("Case refs:", case_refs)
            print("Main doc IDs:", main_doc_ids)
            print("All Docs (with titles):", all_docs)
            print("Some Docs (with titles):", some_docs)


            # 6. final docs intersection
            final_docs = get_final_docs_union(all_docs, some_docs)
            print("Final Docs (with titles):", final_docs)

            doc_titles = [doc['case_title'] for doc in final_docs]
            yield "event: doc_titles\ndata: {}\n\n".format(json.dumps(doc_titles))

            # 7. get summaries for final docs (without paragraphs, no relevance here)
            doc_ids = [doc["id"] for doc in final_docs]  # extract the IDs
            all_case_laws_summaries = get_all_case_law_summaries(doc_ids)

            # 8. gemini to find relevant cases
            relevant_cases = get_relevant_cases(all_case_laws_summaries, memo_text, legal_problem, case_refs)

            # Stream them now
            yield "event: relevant_cases\ndata: {}\n\n".format(json.dumps(relevant_cases))

            relevant_cases_summary_with_paragraph = get_cases_summary_with_paragraphs(relevant_cases)

            xml_relevant_cases_summary_with_paragraph = to_xml_case_law_summaries_with_paragraphs(relevant_cases_summary_with_paragraph)

            print(estimate_token_count(xml_relevant_cases_summary_with_paragraph))

            final_memo_box = {"text": ""}
            yield from stream_final_memo(
                final_memo_box,
                legal_problem,
                memo_text,
                xml_relevant_cases_summary_with_paragraph,
                relevant_cases
            )
            final_memo_text = final_memo_box["text"]  # entire final memo
            # 6) Now we construct a conversation object that the frontend can use for chat
            
            yield f"event: final_memo\ndata: {final_memo_text}\n\n"
                    
            conversation = []

            # # 7) Send that conversation object. The frontend can store it in memory for chat usage.
            yield f"event: conversation\ndata: {json.dumps(conversation)}\n\n"

            # 6. SSE completed
            yield "event: done\ndata: All steps complete\n\n"

        except Exception as e:
            traceback.print_exc()
            yield f"event: error\ndata: {str(e)}\n\n"


    # Return a streaming response with the SSE MIME type
    return Response(sse_generator(legal_problem), mimetype='text/event-stream')


@app.route('/chat', methods=['POST'])
def chat_sse():
    data = request.get_json()
    conversation = data.get('conversation', [])
    relevant_cases = data.get('relevant_cases', {"case": []})
    user_query = data.get('user_task', '').strip()
    legal_problem = data.get('dispute', '').strip()
    memo = data.get('final_memo', '').strip()


    print(user_query)

    if not user_query:
        return jsonify({'error': 'No user task provided'}), 400
        

    def sse_generator(user_query, conversation, relevant_cases, legal_problem, memo):
        try:
            relevant_cases_summary_with_paragraph = get_cases_summary_with_paragraphs(relevant_cases)
            xml_relevant_cases_summary_with_paragraph = to_xml_case_law_summaries_with_paragraphs(relevant_cases_summary_with_paragraph)
            chat_box = {"text": ""}
            # actual chat
            yield from stream_chat(chat_box, user_query, conversation, xml_relevant_cases_summary_with_paragraph, relevant_cases, legal_problem, memo)
            chat_box_text = chat_box["text"]

            case_refs = parse_chat_text(chat_box_text)
            relevant_cases = update_relevant_cases(relevant_cases, case_refs)
            
            relevant_cases_summary_with_paragraph = get_cases_summary_with_paragraphs(relevant_cases)
            xml_relevant_cases_summary_with_paragraph = to_xml_case_law_summaries_with_paragraphs(relevant_cases_summary_with_paragraph)
            
            conversation = update_conversation(conversation, chat_box_text, user_query)
            
            yield "event: relevant_cases\ndata: {}\n\n".format(json.dumps(relevant_cases))
            yield f"event: conversation\ndata: {json.dumps(conversation)}\n\n"
            yield "event: done\ndata: All steps complete\n\n"

        except Exception as e:
            traceback.print_exc()
            yield f"event: error\ndata: {str(e)}\n\n"

    # Return a streaming response with the SSE MIME type
    return Response(sse_generator(user_query, conversation, relevant_cases, legal_problem, memo), mimetype='text/event-stream')

    
@app.route('/get_case_details', methods=['POST'])
def get_case_details():
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        analysis_reasoning_ids = data.get('analysis_reasoning_ids', [])

        print(document_id)
        print(analysis_reasoning_ids)

        if not document_id:
            return jsonify({'error': 'No document ID provided'}), 400

        with driver.session() as session:
            # Fetch case summary with highlighting and referred cases
            case_summary = session.read_transaction(
                get_case_summary, document_id, analysis_reasoning_ids
            )

            # If no analysis_reasoning_ids provided, remove 'cases_referred' to prevent infinite loops
            if not analysis_reasoning_ids:
                case_summary.pop('cases_referred', None)

            # Fetch case text (paragraphs)
            case_text = session.read_transaction(
                get_case_text, document_id, analysis_reasoning_ids
            )

        response = {
            'case_summary': case_summary,
            'case_text': case_text
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error in get_case_details: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while fetching case details.'}), 500



# def task_A(memo_text):
#     """
#     1) parse_initial_memo(memo_text)
#     2) query_full_text_index(...)
#     3) get_related_docs(...)
#     """
#     case_refs = parse_initial_memo(memo_text)
#     main_doc_ids = query_full_text_index(case_refs)
#     all_docs = get_related_docs(main_doc_ids)
#     # some_docs_fulltext = query_summary_fulltext_index(memo_text)
#     return case_refs, main_doc_ids, all_docs

# def task_B(memo_text):
#     """
#     1) get_embed(memo_text)
#     2) query_vector_index(...)
#     """
#     memo_embed = get_embed(memo_text)
#     some_docs = query_vector_index(memo_embed)
#     return memo_embed, some_docs




def stream_initial_memo(memo_box, legal_problem):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""
You are a legal research assistant tasked with analyzing and providing insights on a given legal Proposition. Your goal is to conduct thorough legal research and present a comprehensive and well-reasoned legal memo that mirrors the depth and precision of professional legal analyses that can assist a legal professional in addressing the given Proposition. 

Follow the steps below meticulously to ensure a comprehensive analysis.


1. **Review the Legal Proposition:** Carefully read and understand the provided legal Proposition to grasp all relevant facts and legal questions.

<legal_Proposition>
{legal_problem}
</legal_Proposition>

2. Now, follow the legal research methodology outlined below.

a) **Identify the Research Proposition:** 
      - Break down the Proposition into specific legal questions that need to be addressed.

b) **Collect Legal Sources:** 
      - **Statutes:** Enumerate specific statutes, sections, and legal provisions relevant to each identified issue.
      - **Case Laws:** Include pertinent case laws, especially from the Supreme Court of India, that have established significant legal precedents related to the issues.

c) **Synthesize Legal Principles:** 
      - Extract key legal concepts and principles from the collected sources. Provide clear definitions and explanations for each identified principle.
      - Explain how these principles interrelate and apply to the given Proposition.
      - For each relevant case law, provide a concise summary of the court's ruling, and the rationale behind the decision.
      - Analyze how the principles established in each case apply to the current legal Proposition.
      - Highlight similarities and distinctions between the cases and the present scenario to build a robust legal argument.
      - Develop a coherent understanding of the legal issue by logically connecting the facts to the legal doctrines.


3. Now, Identify highly relevant case laws, preferably from the Supreme Court of India, applicable to this legal Proposition. For each case, provide a comprehensive explanation of its relevance, focusing on key legal principles and their application to the current Proposition, demonstrating how it influences the interpretation or application of the law in this context.


Follow these instructions carefully to produce a well-structured and legally sound memo ensuring comprehensive coverage, deep analysis, and clear linkage between facts and legal principles. The memo should provide a thorough examination of each legal issue, supported by relevant statutes, case laws, and clear logical reasoning.

Analyze the Proposition and research thoroughly. Identify the key legal issues, relevant laws, and applicable precedents. Consider how the facts of the case relate to the legal principles identified in your research.

Structure your memo using the following outline:

1. Issues Involved
    - List each legal question clearly and succinctly.
    - Ensure that each issue is directly derived from the facts of the legal Proposition.

2. Discussion/Reasoning
Provide a detailed legal analysis here. This should include:
    - Clearly explain the relevant legal principles, statutes, and case law. Integrate relevant case laws, summarizing their holdings and applying their principles to the Proposition at hand.

    - Carefully examine how the specific facts or questions presented in the legal Proposition interact with the legal principles. Demonstrate how the legal principles influence the outcome of each issue based on the provided facts. Provide hypothetical scenarios or counterexamples if necessary to highlight the strengths of your analysis. Explain your reasoning and how these principles lead to potential conclusions or answers.

    - Discuss potential arguments, counterarguments, or alternative interpretations of the law. Where applicable, analyze differing judicial opinions or interpretations related to the legal issues. Critically evaluate these perspectives, explaining why they may or may not apply to the case. Reinforce your conclusions by addressing and refuting opposing viewpoints where applicable.

    - Ensure each issue is addressed in a logical and coherent manner, with clear connections between facts and legal standards.

Important: Whenever you cite any case laws in this section, mention the case law title within <<Case Name (Year)>> tags.

3. Findings/Conclusion
    - Provide a clear, concise summary of the legal opinion based on the analysis. 
    - Provide clear and concise conclusions for each issue identified, supported by the reasoning discussed.

When drafting your memo:
Use relevant legal sources: Cite cases, statutes, and other authoritative sources from the provided research. Whenever you cite any case laws, mention the case law title within <<Case Title (Year)>> tags.

Use legal language: Employ formal legal language, terminology and phrasing and maintain a formal, professional tone appropriate for professional legal memos. Maintain an objective and impartial tone, avoiding colloquialisms and subjective statements. Use headings and subheadings to organize content logically, enhancing readability.

Structure of the opinion: Ensure your memo follows a logical flow. Begin with a clear statement of the issues, followed by a thorough discussion of the law and its application to the facts. Conclude with a well-reasoned finding or opinion.

Present your draft memo using the following XML tags:

<legal_memo>
<issues_involved>
[Clearly state the legal questions that need to be addressed.]
</issues_involved>

<discussion_reasoning>
[Provide a detailed analysis of the law and its application to the facts.
Important: Whenever you cite any case laws in this section, mention the case law title within <<Case Title (Year)>> tags.]
</discussion_reasoning>

<findings_conclusion>
[Summarize your legal opinion based on your analysis.]
</findings_conclusion>
</legal_memo>

Before finalizing your memo, review and refine your analysis to ensure it aligns with the highest legal standards:

- **Review for Completeness:** Ensure all key legal issues identified are thoroughly addressed.
- **Check Logical Flow:** Verify that the memo flows logically from issues to discussion to conclusions.
- **Ensure Accuracy:** Confirm that all legal citations are accurate and correctly applied. Consider whether each argument is supported by relevant legal authorities.
- **Proofread:** Correct any grammatical or typographical errors to maintain professionalism.

Remember to maintain a professional and objective tone throughout your analysis. If you encounter any ambiguities in the legal Proposition, state your assumptions clearly. Your goal is to provide a comprehensive and well-structured memo that could assist a legal professional in addressing the given Proposition. Ensure that your memo is comprehensive, well-reasoned, and adheres to professional legal standards. Focus on clarity, logical argumentation, and proper use of legal authorities.

"""
    # Stream the output in chunks
    # Each iteration yields partial text of the response as it is generated.
    with client.messages.stream(
        model="claude-3-5-haiku-20241022",
        max_tokens=2048,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text_chunk in stream.text_stream:
            # accumulate
            memo_box['text'] += text_chunk
            # Send SSE chunk
            yield f"event: partial_memo\ndata: {json.dumps(text_chunk)}\n\n"

def parse_initial_memo(initial_memo):
    """
    Parse case references in the format: <<Case Name (Year)>>
    Extracts both the full case reference "Case Name (Year)" and the year as an integer.
    Returns a list of tuples: [(case_ref, year), ...] where case_ref includes the year in parentheses.
    """
    pattern = r'<<(.*?)\((\d{4})\)>>'
    matches = re.findall(pattern, initial_memo)
    # matches: list of tuples (case_name_without_parenthesis, year_str)
    # We reconstruct the full name with year as "CaseName (Year)"
    case_refs = []
    for name, year_str in matches:
        full_case_name = f"{name.strip()} ({year_str})"
        year = int(year_str)
        case_refs.append((full_case_name, year))
    return case_refs

def escape_lucene_special_chars(text):
    # Define a list of Lucene special characters.
    # Note: Order matters – process multi-character tokens like '&&' and '||' first.
    special_chars = ['&&', '||', '+', '-', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':', '\\', '/']
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text

# Example usage in your query function:
def query_full_text_index(case_refs):
    doc_ids = []
    with driver.session() as session:
        for (case_name, case_year) in case_refs:
            # Escape the special characters in the case name
            escaped_case_name = escape_lucene_special_chars(case_name)
            query = """
            CALL db.index.fulltext.queryNodes("doc_case_title", $search_term, {mode: "PHRASE"}) YIELD node, score
            RETURN node, score
            ORDER BY score DESC
            LIMIT 5
            """
            result = session.run(query, search_term=escaped_case_name)
            candidates = [(r['node'], r['node'].get('case_year', -1)) for r in result]
            filtered = []
            for (node, y) in candidates:
                if len(filtered) == 2:
                    break
                if case_year == -1:
                    filtered.append(node.id)
                else:
                    if y in [case_year, case_year + 1, case_year - 1]:
                        filtered.append(node.id)
            doc_ids.extend(filtered)
    return list(set(doc_ids))



def get_related_docs(main_docs):
    """
    Given a list of doc IDs, fetch those documents plus any that cite them or are cited by them.
    Return a list of dicts: [ { id: <doc_id>, case_title: <title> }, ... ].
    """
    with driver.session() as session:
        query = """
MATCH (d:Document)
WHERE id(d) IN $document_ids
OPTIONAL MATCH (d)-[:CITES]->(cited:Document)
OPTIONAL MATCH (d)<-[:CITES]-(citing:Document)
WITH COLLECT(DISTINCT d) + COLLECT(DISTINCT cited) + COLLECT(DISTINCT citing) AS level1_docs

UNWIND level1_docs AS doc1
OPTIONAL MATCH (doc1)-[:CITES]->(doc1_cited:Document)
OPTIONAL MATCH (doc1)<-[:CITES]-(doc1_citing:Document)
WITH level1_docs, 
     COLLECT(DISTINCT doc1_cited) AS doc1_cited_list, 
     COLLECT(DISTINCT doc1_citing) AS doc1_citing_list

WITH level1_docs + doc1_cited_list + doc1_citing_list AS all_docs
UNWIND all_docs AS doc
WITH COLLECT(DISTINCT doc) AS all_docs
RETURN [doc IN all_docs | { id: id(doc), case_title: doc.case_title }] AS all_doc_info
        """
        result = session.run(query, document_ids=main_docs)
        record = result.single()
        if record:
            return record['all_doc_info']
        else:
            return []


def get_embed(text):
    """
    Create an embedding for the given text using OpenAI Embeddings API.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text.replace("\n", "  "),
        model="text-embedding-3-large"
    )
    return response.data[0].embedding


def query_vector_index(embedding):
    """
    Query the vector index for relevant documents, returning
    a list of dicts: [ { id: <doc_id>, case_title: <title> }, ... ].
    """
    with driver.session() as session:
        query = """
        CALL db.index.vector.queryNodes('full_summary_vector_idx', 500, $embedding) 
        YIELD node, score
        RETURN id(node) AS id, node.case_title AS case_title
        """
        result = session.run(query, embedding=embedding)
        return [
            {'id': record['id'], 'case_title': record['case_title']}
            for record in result
        ]


def get_final_docs_union(all_docs, some_docs):
    """
    final_docs must contain the union between:
      (intersection between all_docs & some_docs)  U  (the docs corresponding to main_doc_ids)
    """

    # 1. Create dictionaries keyed by doc ID for quick lookup
    all_docs_dict = {doc['id']: doc for doc in all_docs}
    some_docs_dict = {doc['id']: doc for doc in some_docs}

    # 2. Find the IDs that appear in both all_docs and some_docs
    common_ids = set(all_docs_dict.keys()) & set(some_docs_dict.keys())
    intersection_docs = [all_docs_dict[doc_id] for doc_id in common_ids]


    # 4. Combine intersection_docs and main_docs_objs, ensuring uniqueness by doc ID
    final_docs_dict = {}

    for doc in intersection_docs:
        final_docs_dict[doc['id']] = doc

    # for doc in main_docs_objs:
    #     final_docs_dict[doc['id']] = doc

    # 5. Convert dict values back to a list
    final_docs = list(final_docs_dict.values())

    return final_docs


def get_case_law_summaries(tx, document_ids):
    if not document_ids:
        return []
    query = """
    MATCH (d:Document)
    WHERE id(d) IN $document_ids
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(bf:Background_facts)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(li:Legal_issues)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(arg:Arguments)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(do:Decision_order)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(dco:Dissenting_concurring_opinions)
    WITH d, bf, do,
        COLLECT(DISTINCT {issue: li.final_text}) AS legal_issues,
        COLLECT(DISTINCT {argument: arg.final_text}) AS arguments,
        COLLECT(DISTINCT {discussion_id:id(ar), discussion: ar.final_text}) AS analysis_reasoning,
        COLLECT(DISTINCT {opinion: dco.final_text}) AS dissenting_concurring
    RETURN d, bf, do, legal_issues, arguments, analysis_reasoning, dissenting_concurring
    """
    result = tx.run(query, document_ids=document_ids)
    
    summaries = []
    for record in result:
        d = record['d']
        bf = record['bf']
        do = record['do']
        legal_issues = record['legal_issues']
        arguments = record['arguments']
        analysis_reasoning = record['analysis_reasoning']
        dissenting_concurring = record['dissenting_concurring']

        # Rebuild the summary in a consistent, logical order:
        summary = {
            "document_id": d.id if d else None,
            "case_title": d.get('case_title', '') if d else '',
            "background_facts": bf['final_text'] if bf and 'final_text' in bf else '',
            "legal_issues": [issue for issue in legal_issues if issue.get('issue')],
            "arguments": [arg for arg in arguments if arg.get('argument')],
            "analysis_reasoning": [ar for ar in analysis_reasoning if ar.get('discussion')],
            "decision_order": do['final_text'] if do and 'final_text' in do else '',
            "dissenting_concurring": [dco for dco in dissenting_concurring if dco.get('opinion')]
        }

        summaries.append(summary)

    return summaries


def get_all_case_law_summaries(document_ids):
    with driver.session() as session:
        return get_case_law_summaries(session, document_ids)


def to_xml_case_law_summaries(case_law_summaries):
    """
    Convert the list of case law summary dictionaries to an XML string.
    Each element in case_law_summaries is expected to have this structure:
      {
          "document_id": int,
          "case_title": str,
          "background_facts": str,
          "legal_issues": [{"issue": ...}, ...],
          "arguments": [{"argument": ...}, ...],
          "analysis_reasoning": [{"discussion_id":..., "discussion":...}, ...],
          "decision_order": str,
          "dissenting_concurring": [{"opinion": ...}, ...]
      }
    """
    xml_output = ["<court_judgement_summaries>"]
    for summary in case_law_summaries:
        xml_output.append("  <judgement>")
        # Document ID
        xml_output.append(f"    <doc_id>{summary.get('document_id', '')}</doc_id>")
        # Case Title
        xml_output.append(f"    <case_title>{summary.get('case_title', '')}</case_title>")
        # Background Facts
        xml_output.append(f"    <background_facts>{summary.get('background_facts', '')}</background_facts>")

        # Legal Issues
        xml_output.append("    <legal_issues>")
        for item in summary.get('legal_issues', []):
            issue_text = item.get('issue', '')
            # Only generate a tag if there's an actual value
            if issue_text:
                xml_output.append(f"      <issue>{issue_text}</issue>")
        xml_output.append("    </legal_issues>")

        # Arguments
        xml_output.append("    <arguments>")
        for arg_item in summary.get('arguments', []):
            arg_text = arg_item.get('argument', '')
            if arg_text:
                xml_output.append(f"      <argument>{arg_text}</argument>")
        xml_output.append("    </arguments>")

        # Analysis Reasoning
        xml_output.append("    <analysis_reasoning>")
        for ar_item in summary.get('analysis_reasoning', []):
            discussion_id = ar_item.get('discussion_id', '')
            discussion_text = ar_item.get('discussion', '')
            if discussion_text:
                xml_output.append("      <analysis>")
                xml_output.append(f"        <discussion_id>{discussion_id}</discussion_id>")
                xml_output.append(f"        <discussion>{discussion_text}</discussion>")
                xml_output.append("      </analysis>")
        xml_output.append("    </analysis_reasoning>")

        # Decision Order
        xml_output.append(f"    <decision_order>{summary.get('decision_order', '')}</decision_order>")

        # Dissenting / Concurring
        xml_output.append("    <dissenting_concurring>")
        for dco_item in summary.get('dissenting_concurring', []):
            opinion_text = dco_item.get('opinion', '')
            if opinion_text:
                xml_output.append(f"      <opinion>{opinion_text}</opinion>")
        xml_output.append("    </dissenting_concurring>")

        xml_output.append("  </judgement>")
    xml_output.append("</court_judgement_summaries>")
    return "\n".join(xml_output)


def get_relevant_cases(all_case_laws_summaries, memo, legal_problem, case_refs):
    genai.configure(api_key=GEMINI_API_KEY)

    # Convert the retrieved case law summaries to XML
    case_law_summaries_xml = to_xml_case_law_summaries(all_case_laws_summaries)

    prompt = f"""
You are an advanced legal research assistant AI tasked with analyzing a legal research memo and a legal Proposition, then selecting the most relevant case laws from a provided set of summaries. Your analysis will be crucial for legal professionals to understand the context and implications of the given legal situation.

Carefully review the following information:

1. Read and analyze the following legal research memo:

<legal_research_memo>
{memo}
</legal_research_memo>

2. Review the provided legal Proposition:

<legal_Proposition>
{legal_problem}
</legal_Proposition>

3. Review the case titles Mentioned in the Memo:
<memo_case_titles>
{case_refs}
</memo_case_titles>

4. Examine the following case law summaries. Each case law summary has the following structure:
- One unique doc_id for the entire case law
- Multiple sections within each summary
- Discussion sections with unique discussion_ids

<case_law_summaries>
{case_law_summaries_xml}
</case_law_summaries>

Now, follow these steps to analyze the information and select relevant case laws:

1. Analyze the legal research memo and legal Proposition. Identify key issues, legal principles.

2. Review the case law summaries and identify the cases mentioned in the memo. Note their corresponding doc_ids, and the most relevant discussion_id from the case law summaries provided.

3. Select additional cases from the summaries, if required. Include cases that offer different perspectives or interpretations, considering both supporting and opposing viewpoints. Ensure that your selection covers the issues and analysis identified in the memo.

4. Select atleast 10 case laws, including those mentioned in the memo. The exact number should be based on the complexity of the legal Proposition.

5. For each selected case, provide the following information:
   - The doc_id
   - The most relevant and applicable discussion_id
   - A comprehensive explanation of its relevance, covering:
     a. Key legal principles and their application
     b. How this case influences the interpretation or application of the law in this context

6. Ensure that no doc_id is repeated in your selection.

7. Double-check that all cases mentioned in the memo are included in your final selection.

Before providing your final output, wrap your analysis in <legal_analysis> tags:
1. Quote key passages from the memo and legal Proposition.
2. All cases mentioned in the memo with their corresponding doc_ids, and the most relevant discussion_id from the case law summaries provided.
3. Relevance and Applicability of case law summaries to the memo and legal Proposition.
4. Explain your reasons for selecting case laws, including:
    - The number of selected case laws based on the complexity of the legal Proposition.
    - How the selected cases cover issues and analysis from the memo.
    - Your consideration of supporting and opposing viewpoints.

This will help ensure a thorough and well-reasoned selection of case laws.


Use the following format for your output:

<memo_cases>
[List the doc_ids of cases mentioned in the memo]
</memo_cases>

<selected_case_laws>
    <case>
        <doc_id>[DOCUMENT_ID]</doc_id>
        <case_title>[CASE_TITLE]</case_title>
        <discussion_id>[Most relevant DISCUSSION_ID]</discussion_id>
        <relevance>
            [Comprehensive explanation of relevance]
        </relevance>
    </case>
    <!-- Repeat <case> tags for each selected case law (atleast 10 in total, based on the complexity of the legal Proposition) -->
</selected_case_laws>

<number_of_selected_case_laws>[Number of case laws selected]</number_of_selected_case_laws>

Ensure that your final selection and analysis comprehensively address all aspects of the legal research memo and Proposition, providing a well-rounded perspective on the legal issues at hand.
"""
    

    print(prompt)

    # Create the model
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    print("Raw Gemini Response:\n", response)

    # Regex approach
    # 1. Extract everything between <case> ... </case>
    case_pattern = re.compile(r"<case>(.*?)</case>", re.DOTALL)
    # 2. For each <case> block, extract doc_id, discussion_id, relevance
    doc_id_pattern = re.compile(r"<doc_id>(.*?)</doc_id>", re.DOTALL)
    case_title_pattern = re.compile(r"<case_title>(.*?)</case_title>", re.DOTALL)
    discussion_id_pattern = re.compile(r"<discussion_id>(.*?)</discussion_id>", re.DOTALL)
    relevance_pattern = re.compile(r"<relevance>(.*?)</relevance>", re.DOTALL)

    relevant_cases = {"case": []}
    case_blocks = case_pattern.findall(response.text)

    for block in case_blocks:
        # Extract doc_id
        doc_id_match = doc_id_pattern.search(block)
        case_title_match = case_title_pattern.search(block)
        discussion_id_match = discussion_id_pattern.search(block)
        relevance_match = relevance_pattern.search(block)

        doc_id_str = doc_id_match.group(1).strip() if doc_id_match else ""
        case_title_str = case_title_match.group(1).strip() if case_title_match else ""
        discussion_id_str = discussion_id_match.group(1).strip() if discussion_id_match else ""
        relevance_str = relevance_match.group(1).strip() if relevance_match else ""

        # Convert doc_id, discussion_id to integers if possible
        try:
            doc_id = int(doc_id_str)
        except ValueError:
            doc_id = None

        try:
            discussion_id = int(discussion_id_str)
        except ValueError:
            discussion_id = None

        case_dict = {
            "doc_id": doc_id,
            "case_title": case_title_str,
            "discussion_id": discussion_id,
            "relevance": relevance_str
        }
        relevant_cases["case"].append(case_dict)

    return relevant_cases

def get_case_summary_chat(tx, document_id):
    query = """
    MATCH (d:Document)
    WHERE id(d) = $document_id
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(bf:Background_facts)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(li:Legal_issues)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(arg:Arguments)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(do:Decision_order)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(dco:Dissenting_concurring_opinions)
    WITH d, bf, do,
        COLLECT(DISTINCT {issue: li.final_text}) AS legal_issues,
        COLLECT(DISTINCT {argument: arg.final_text}) AS arguments,
        COLLECT(DISTINCT {discussion: ar.final_text, discussion_id:id(ar)}) AS analysis_reasoning,
        COLLECT(DISTINCT {opinion: dco.final_text}) AS dissenting_concurring
    RETURN {
        document_id: id(d),
        case_title: d.case_title,
        eq_citations: coalesce(d.eq_citations, []),
        background_facts: bf.final_text,
        legal_issues: [iss IN legal_issues WHERE iss.issue IS NOT NULL | iss],
        arguments: [arg IN arguments WHERE arg.argument IS NOT NULL | arg],
        analysis_reasoning: [ar IN analysis_reasoning WHERE ar.discussion IS NOT NULL | ar],
        decision_order: do.final_text,
        dissenting_concurring: [dco IN dissenting_concurring WHERE dco.opinion IS NOT NULL | dco]
    } AS summary
    """
    result = tx.run(query, document_id=document_id)
    record = result.single()
    return record['summary'] if record else {}

def get_paragraphs_for_analysis_reasoning(tx, analysis_reasoning_ids):
    if not analysis_reasoning_ids:
        return {}
    query = """
    MATCH (ar:Analysis_reasoning)
    WHERE id(ar) IN $analysis_reasoning_ids
    MATCH (ar)-[:PARA_REF]->(p:Paragraph)
    RETURN id(ar) AS ar_id, p.paragraph_number AS para_num, p.paragraph_text AS text
    ORDER BY ar_id, para_num
    """
    result = tx.run(query, analysis_reasoning_ids=analysis_reasoning_ids)
    paragraphs = {}
    for record in result:
        ar_id = record['ar_id']
        if ar_id not in paragraphs:
            paragraphs[ar_id] = []
        paragraphs[ar_id].append({'paragraph': record['text']})
    return paragraphs

def get_single_case_summary_with_paragraphs(document_id, discussion_id):
    """
    Retrieves the summary for a single case (identified by document_id) 
    and includes the relevant paragraphs for the specified discussion_id.
    """
    with driver.session() as session:
        summary = get_case_summary_chat(session, document_id)  # summary is a dict of case details
        paragraphs = get_paragraphs_for_analysis_reasoning(session, [discussion_id])
        
    organized_summary = {
        "document_id": summary.get("document_id"),
        "case_title": summary.get("case_title"),
        "eq_citations": summary.get("eq_citations"),
        "background_facts": summary.get("background_facts"),
        "legal_issues": summary.get("legal_issues"),
        "arguments": summary.get("arguments"),
        "analysis_reasoning": summary.get("analysis_reasoning"),
        "decision_order": summary.get("decision_order"),
        "dissenting_concurring": summary.get("dissenting_concurring"),
        "relevant_paragraphs": paragraphs.get(discussion_id, [])  # paragraphs from the specified discussion_id
    }
    
    return organized_summary


def get_cases_summary_with_paragraphs(relevant_cases):
    case_summaries = []
    
    for case_info in relevant_cases["case"]:
        doc_id = case_info.get("doc_id")
        discussion_ids = case_info.get("discussion_id")
        
        if doc_id is None or not discussion_ids:
            continue
        
        if isinstance(discussion_ids, int):
            discussion_ids = [discussion_ids]
        
        for discussion_id in discussion_ids:
            summary_with_paragraphs = get_single_case_summary_with_paragraphs(doc_id, discussion_id)
            case_summaries.append(summary_with_paragraphs)
    
    return case_summaries


import xml.etree.ElementTree as ET

def to_xml_case_law_summaries_with_paragraphs(case_law_summaries):
    root = ET.Element("court_judgement_summaries")
    
    for summary in case_law_summaries:
        judgement = ET.SubElement(root, "judgement")
        
        doc_id = ET.SubElement(judgement, "doc_id")
        doc_id.text = str(summary.get('document_id', ''))
        
        case_title = ET.SubElement(judgement, "case_title")
        case_title.text = summary.get('case_title', '')
        
        citations = ET.SubElement(judgement, "citations")
        citations.text = ", ".join(summary.get('eq_citations', [])) if isinstance(summary.get('eq_citations'), list) else summary.get('eq_citations', '')
        
        background_facts = ET.SubElement(judgement, "background_facts")
        background_facts.text = summary.get('background_facts', '')
        
        # Legal Issues
        legal_issues = ET.SubElement(judgement, "legal_issues")
        for li in summary.get('legal_issues', []):
            issue = ET.SubElement(legal_issues, "issue")
            issue.text = li.get('issue', '')
        
        # Arguments
        arguments = ET.SubElement(judgement, "arguments")
        for arg in summary.get('arguments', []):
            argument = ET.SubElement(arguments, "argument")
            argument.text = arg.get('argument', '')
        
        # Analysis Reasoning
        analysis_reasoning = ET.SubElement(judgement, "analysis_reasoning")
        for ar_item in summary.get('analysis_reasoning', []):
            analysis = ET.SubElement(analysis_reasoning, "analysis")
            
            discussion_id = ET.SubElement(analysis, "discussion_id")
            discussion_id.text = str(ar_item.get('discussion_id', ''))
            
            discussion = ET.SubElement(analysis, "discussion")
            discussion.text = ar_item.get('discussion', '')
            
            relevant_chunk = ET.SubElement(analysis, "relevant_chunk_from_the_judgement")
            paragraphs = summary.get('relevant_paragraphs', [])
            for para in paragraphs:
                para_text = ET.SubElement(relevant_chunk, "paragraph")
                para_text.text = para.get('paragraph', '')
        
        # Decision Order
        decision_order = ET.SubElement(judgement, "decision_order")
        decision_order.text = summary.get('decision_order', '')
        
        # Dissenting / Concurring
        dissenting_concurring = ET.SubElement(judgement, "dissenting_concurring")
        for dco in summary.get('dissenting_concurring', []):
            opinion = ET.SubElement(dissenting_concurring, "opinion")
            opinion.text = dco.get('opinion', '')
    
    return ET.tostring(root, encoding='unicode')


def stream_final_memo(memo_box, leg_prob, initial_memo, xml_relevant_cases_summary_with_paragraph, relevant_cases):
    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""You are a legal research assistant tasked with analyzing and providing insights on a given legal Proposition. Your goal is to conduct thorough legal research and present a comprehensive and well-reasoned legal memo that mirrors the depth and precision of professional legal analyses that can assist a legal professional. 

Follow the steps below meticulously to ensure a comprehensive analysis.

1. **Review the Legal Proposition:** Carefully read and understand the provided legal Proposition to grasp all relevant facts and legal questions.

<legal_Proposition>
{leg_prob}
</legal_Proposition>

2. Now, follow the legal research methodology outlined below.

a) **Identify the Research Proposition:** 
      - Break down the Proposition into specific legal questions that need to be addressed.

b) **Collect Legal Sources:** 
      - **Statutes:** Enumerate specific statutes, sections, and legal provisions relevant to each identified issue.
      - **Case Laws:** Include pertinent case laws, especially from the Supreme Court of India, that have established significant legal precedents related to the issues.

c) **Synthesize Legal Principles:** 
      - Extract key legal concepts and principles from the collected sources. Provide clear definitions and explanations for each identified principle.
      - Explain how these principles interrelate and apply to the given Proposition.
      - For each relevant case law, provide a concise summary of the court's ruling, and the rationale behind the decision.
      - Analyze how the principles established in each case apply to the current legal Proposition.
      - Highlight similarities and distinctions between the cases and the present scenario to build a robust legal argument.
      - Develop a coherent understanding of the legal issue by logically connecting the facts to the legal doctrines.


Follow these instructions carefully to produce a well-structured and legally sound memo ensuring comprehensive coverage, deep analysis, and clear linkage between facts and legal principles. The memo should provide a thorough examination of each legal issue, supported by relevant statutes, case laws, and clear logical reasoning.

Analyze the Proposition and research thoroughly. Identify the key legal issues, relevant laws, and applicable precedents. Consider how the facts of the case relate to the legal principles identified in your research.

Structure your memo using the following outline:

1. Issues Involved
    - List each legal question clearly and succinctly.
    - Ensure that each issue is directly derived from the legal Proposition.

2. Discussion/Reasoning
Provide a detailed legal analysis here. This should include:
    - Clearly explain the relevant legal principles, statutes, and case law. Integrate relevant case laws, summarizing their holdings and applying their principles to the Proposition at hand.

    - Carefully examine how the specific facts or questions presented in the legal Proposition interact with the legal principles. Demonstrate how the legal principles influence the outcome of each issue based on the provided facts. Provide hypothetical scenarios or counterexamples if necessary to highlight the strengths of your analysis. Explain your reasoning and how these principles lead to potential conclusions or answers.

    - Discuss potential arguments, counterarguments, or alternative interpretations of the law. Where applicable, analyze differing judicial opinions or interpretations related to the legal issues. Critically evaluate these perspectives, explaining why they may or may not apply to the case. Reinforce your conclusions by addressing and refuting opposing viewpoints where applicable.

    - Ensure each issue is addressed in a logical and coherent manner, with clear connections between facts and legal standards.

    - Whenever you cite any case laws, include reference to the case law and to the most relevant and applicable discussion section in this format - <<doc_id; case_title; discussion_id>> tag.

3. Findings/Conclusion
    - Provide a clear, concise summary of the legal opinion based on the analysis. 
    - Provide clear and concise conclusions for each issue identified, supported by the reasoning discussed.

When drafting your memo:
Use relevant legal sources: Cite cases, statutes, and other authoritative sources from the research.

Use legal language: Employ formal legal language, terminology and phrasing and maintain a formal, professional tone appropriate for professional legal memos. Maintain an objective and impartial tone, avoiding colloquialisms and subjective statements.

Structure of the opinion: Ensure your memo follows a logical flow. Begin with a clear statement of the issues, followed by a thorough discussion of the law and its application to the facts. Conclude with a well-reasoned finding or opinion.

Present your draft memo using the following structure:

<legal_memo>
<issues_involved>
[Clearly state the legal questions that need to be addressed.]
</issues_involved>

<discussion_reasoning>
[Provide a detailed analysis of the law and its application to the facts.
Whenever you cite any case laws, include reference to the case law and to the most relevant and applicable discussion section in this format - <<doc_id; case_title; discussion_id>> tag.]
</discussion_reasoning>

<findings_conclusion>
[Summarize your legal opinion based on your analysis.]
</findings_conclusion>
</legal_memo>

Before finalizing your memo, review and refine your analysis to ensure it aligns with the highest legal standards:

- **Review for Completeness:** Ensure all key legal issues identified are thoroughly addressed.
- **Check Logical Flow:** Verify that the memo flows logically from issues to discussion to conclusions.
- **Ensure Accuracy:** Confirm that all legal citations are accurate and correctly applied. Consider whether each argument is supported by relevant legal authorities. Whenever you cite any case laws, include reference to the case law and to the most relevant and applicable discussion section in this format - <<doc_id; case_title; discussion_id>> tag.
- **Proofread:** Correct any grammatical or typographical errors to maintain professionalism.

Remember to maintain a professional and objective tone throughout your analysis. If you encounter any ambiguities in the legal Proposition, state your assumptions clearly. Your goal is to provide a comprehensive and well-structured memo that could assist a legal professional in addressing the given Proposition. Ensure that your memo is comprehensive, well-reasoned, and adheres to professional legal standards. Focus on clarity, logical argumentation, and proper use of legal authorities.
"""

    history_msgs = [
        {"role": "user", "parts": [{"text": f"<legal_Proposition>{leg_prob}</legal_Proposition>"}]},
        {"role": "model", "parts": [{"text": initial_memo}]},
        {"role": "user", "parts": [{"text": xml_relevant_cases_summary_with_paragraph}]},
        # {"role": "model", "parts": relevance_parts},
        {"role": "model", "parts": [{"text": json.dumps(relevant_cases, indent=2)}]},
    ]

    # print(messages)
    # print(history_msgs)

    # Create the model
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=history_msgs
    )
    # Send message with stream=True to receive chunks as they are generated
    response_stream = chat_session.send_message(prompt, stream=True)
    
    # 4) For each chunk, yield it in SSE format
    for chunk in response_stream:
        memo_box['text'] += chunk.text
        print(chunk.text)
        # SSE requires each event to end with a blank line
        # We name the event "partial_final_memo" so the frontend can route it
        yield f"event: partial_final_memo\ndata: {json.dumps(chunk.text)}\n\n"



def stream_chat(chat_box, query, conversation, xml_relevant_cases_summary_with_paragraph, relevant_cases, legal_problem, memo):
    genai.configure(api_key=GEMINI_API_KEY)
    history_msgs = []
    history_msgs.append({"role": "user", "parts": [{"text": xml_relevant_cases_summary_with_paragraph}]})
    history_msgs.append({"role": "model", "parts": [{"text": json.dumps(relevant_cases, indent=2)}]})
    history_msgs.append({"role": "user", "parts": [{"text": legal_problem}]})
    history_msgs.append({"role": "model", "parts": [{"text": memo}]})

    for turn in conversation:
        role = turn.get('role', 'user')
        parts = turn.get('parts', [])
        content = "".join(parts)
        if role == 'user':
            history_msgs.append({"role": "user", "parts": [{"text": content}]})
        else:
            history_msgs.append({"role": "model", "parts": [{"text": content}]})

    from google.ai.generativelanguage_v1beta.types import content

    # print("content is:", content)
    # print("type(content):", type(content))

    # Create the model
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 4096,
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
#         system_instruction="""You are an advanced legal research assistant designed to analyze complex legal Propositions and provide insightful, professional-grade analysis. Your primary goal is to assist legal professionals by conducting thorough research and offering well-reasoned insights.

# Whenever you cite any case laws, include reference to the case law and to the most relevant and applicable discussion section in this format - <<doc_id; case_title; discussion_id>> tag.

# Before providing your final output, Think step-by-step and provide your chain of thought in <thinking> tags.

# This step is crucial. It's OK for this section to be quite long.

# After your thinking, present your final output in <output> tags. Your output should be clear, and directly relevant to assisting a legal professional.

# Whenever you cite any case laws, include reference to the case law and to the most relevant and applicable discussion section in this format - <<doc_id; case_title; discussion_id>> tag.

# Remember to maintain a professional and objective tone throughout. Your goal is to assist a legal professional in addressing the legal Proposition. Focus on clarity, logical argumentation, proper use of legal authorities, and adheres to professional legal standards.

# In every response, Think step-by-step and provide your chain of thought in <thinking> tags. After your thinking, present your final output in <output> tags. Your output should be clear, and directly relevant to assisting a legal professional.
# """,
    )

    chat_session = model.start_chat(
        history=history_msgs
    )

    query = query + """Whenever you cite any case laws, include reference to the case law and to the most relevant and applicable discussion section in this format - <<doc_id; case_title; discussion_id>> tag.

Before providing your final output, Think step-by-step and provide your chain of thought in <thinking> tags.

This step is crucial. It's OK for this section to be quite long.

After your thinking, present your final output in <output> tags. Your output should be clear, and directly relevant to assisting a legal professional."""


# Send message with stream=True to receive chunks as they are generated
    response_stream = chat_session.send_message(query, stream=True)
    
    # 4) For each chunk, yield it in SSE format
    for chunk in response_stream:
        chat_box['text'] += chunk.text
        print(chunk.text)
        # SSE requires each event to end with a blank line
        # We name the event "partial_final_memo" so the frontend can route it
        yield f"event: partial_chat_response\ndata: {json.dumps({'text': chunk.text})}\n\n"


def parse_chat_text(text):
    """
    Parse the chat text to extract citations in the format <<doc_id; case_title; discussion_id>>.
    Organize them into a dictionary with 'case_refs' key.

    Args:
        text (str): The input text containing case citations.

    Returns:
        dict: A dictionary containing a list of case references.
              {
                  "case_refs": [
                      {
                          "doc_id": <int>,
                          "case_title": <str>,
                          "discussion_id": <int>
                      },
                      ...
                  ]
              }
    """
    # Regex pattern to match <<doc_id; case_title; discussion_id>>
    pattern = r'<<\s*(\d+)\s*;\s*(.*?)\s*;\s*(\d+)\s*>>'
    matches = re.findall(pattern, text)
    
    case_refs = []
    for match in matches:
        doc_id = int(match[0])
        case_title = match[1].strip()
        discussion_id = int(match[2])
        case_refs.append({
            "doc_id": doc_id,
            "case_title": case_title,
            "discussion_id": discussion_id
        })
    
    return {"case_refs": case_refs}


def update_relevant_cases(relevant_cases, new_case_refs):
    """
    Update the relevant_cases dictionary with new_case_refs.

    Args:
        relevant_cases (dict): Existing relevant_cases with structure
            {
                "case": [
                    {
                        "doc_id": <int>,
                        "case_title": <str>,
                        "discussion_id": <int> or [<int>, ...]
                    },
                    ...
                ]
            }

        new_case_refs (dict): New case_refs with structure
            {
                "case_refs": [
                    {
                        "doc_id": <int>,
                        "case_title": <str>,
                        "discussion_id": <int>
                    },
                    ...
                ]
            }

    Returns:
        dict: Updated relevant_cases dictionary.
    """
    if "case" not in relevant_cases:
        relevant_cases["case"] = []

    for new_case in new_case_refs.get("case_refs", []):
        doc_id = new_case["doc_id"]
        case_title = new_case["case_title"]
        discussion_id = new_case["discussion_id"]

        # Find if the doc_id already exists in relevant_cases
        existing_case = next((case for case in relevant_cases["case"] if case["doc_id"] == doc_id), None)

        if existing_case:
            # Ensure 'discussion_id' is a list
            if isinstance(existing_case.get("discussion_id"), int):
                existing_case["discussion_id"] = [existing_case["discussion_id"]]
            elif not isinstance(existing_case.get("discussion_id"), list):
                existing_case["discussion_id"] = []

            # Add the discussion_id if it's not already present
            if discussion_id not in existing_case["discussion_id"]:
                existing_case["discussion_id"].append(discussion_id)
        

    return relevant_cases



def update_conversation(actual_convo, chat_box_text, user_query):
    actual_convo.append({
        "role": "user",
        "parts": [user_query]
    })
    actual_convo.append({
        "role": "model",
        "parts": [chat_box_text]
    })
    return actual_convo



def get_case_summary(tx, document_id, analysis_reasoning_ids):
    try:
        # Fetch the main case summary components
        query = """
        MATCH (d:Document)
        WHERE id(d) = $document_id
        OPTIONAL MATCH (d)<-[:SUMMARIZES]-(bf:Background_facts)
        OPTIONAL MATCH (d)<-[:SUMMARIZES]-(li:Legal_issues)
        OPTIONAL MATCH (d)<-[:SUMMARIZES]-(arg:Arguments)
        OPTIONAL MATCH (d)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
        OPTIONAL MATCH (d)<-[:SUMMARIZES]-(do:Decision_order)
        OPTIONAL MATCH (d)<-[:SUMMARIZES]-(dco:Dissenting_concurring_opinions)

        // Fetch referred cases via SUMMARY_CITES relationships
        OPTIONAL MATCH (ar)-[:SUMMARY_CITES]->(cited_doc:Document)
        WHERE id(ar) IN $analysis_reasoning_ids OR $analysis_reasoning_ids IS NULL OR SIZE($analysis_reasoning_ids) = 0
        WITH d, bf, do, li, arg, ar, dco, cited_doc

        // Collect data
        WITH d, bf, do,
            COLLECT(DISTINCT li) AS legal_issues_nodes,
            COLLECT(DISTINCT arg) AS arguments_nodes,
            COLLECT(DISTINCT ar) AS analysis_reasoning_nodes,
            COLLECT(DISTINCT dco) AS dissenting_concurring_nodes,
            COLLECT(DISTINCT cited_doc) AS cited_documents

        // Prepare data
        WITH d, bf, do,
            [li IN legal_issues_nodes | {text: li.final_text, index: coalesce(li.index, 0)}] AS legal_issues,
            [arg IN arguments_nodes | {text: arg.final_text, index: coalesce(arg.index, 0)}] AS arguments,
            [ar IN analysis_reasoning_nodes | {
                text: ar.final_text,
                index: coalesce(ar.index, 0),
                id: id(ar),
                highlight: id(ar) IN $analysis_reasoning_ids
            }] AS analysis_reasoning,
            [dco IN dissenting_concurring_nodes | {text: dco.final_text, index: coalesce(dco.index, 0)}] AS dissenting_concurring,
            cited_documents

        // Prepare cases referred with document IDs
        WITH d, bf, do, legal_issues, arguments, analysis_reasoning, dissenting_concurring,
            [cited_doc IN cited_documents WHERE cited_doc.case_title IS NOT NULL | {
                document_id: id(cited_doc),
                case_title: cited_doc.case_title
            }] AS cases_referred

        RETURN {
            case_title: d.case_title,
            eq_citations: coalesce(d.eq_citations, []),
            background_facts: bf.final_text,
            legal_issues: [issue IN legal_issues WHERE issue.text IS NOT NULL | issue],
            arguments: [arg IN arguments WHERE arg.text IS NOT NULL | arg],
            analysis_reasoning: [ar IN analysis_reasoning WHERE ar.text IS NOT NULL | ar],
            decision_order: do.final_text,
            dissenting_concurring: [dco IN dissenting_concurring WHERE dco.text IS NOT NULL | dco],
            cases_referred: cases_referred
        } AS summary
        """
        result = tx.run(query, document_id=document_id, analysis_reasoning_ids=analysis_reasoning_ids)
        record = result.single()
        return record['summary'] if record else {}
    except Exception as e:
        print(f"Error getting case summary: {str(e)}")
        raise


def get_case_text(tx, document_id, analysis_reasoning_ids):
    try:
        query = """
        MATCH (d:Document)
        WHERE id(d) = $document_id
        MATCH (d)-[:HAS_PARAGRAPH]->(p:Paragraph)
        WITH p
        ORDER BY p.paragraph_number
        OPTIONAL MATCH (p)<-[:PARA_REF]-(ar:Analysis_reasoning)
        RETURN p.paragraph_number AS para_num, p.paragraph_text AS text, id(ar) AS ar_id
        """
        result = tx.run(query, document_id=document_id)
        case_text = ''
        for record in result:
            para_num = record['para_num']
            text = record['text']
            ar_id = record['ar_id']
            if ar_id and ar_id in analysis_reasoning_ids:
                # Wrap the paragraph text with span for highlighting
                case_text += f"<p><span data-summary-cites=\"{ar_id}\">{para_num}. {text}</span></p>\n"
                print(case_text)
            else:
                case_text += f"<p>{para_num}. {text}</p>\n"
        print(case_text)
        return case_text
    except Exception as e:
        print(f"Error getting case text: {str(e)}")
        raise





def estimate_token_count(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


if __name__ == '__main__':
    app.run(debug=True, port=5002)
