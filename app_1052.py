from flask import Flask, request, jsonify, render_template
from neo4j import GraphDatabase
from openai import OpenAI
import openai
import anthropic
import os
import re
import traceback

app = Flask(__name__)

# Load configuration from environment variables
# NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_URI = os.environ.get('NEO4J_URI', 'neo4j+s://f836b6b0.databases.neo4j.io')

NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
#NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'sc_graph_db')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', '58viJiu1S_VTKqmitzn6WnDkaYdcr7WiMrlvAGSzyHY')
#gpodQl3XhiIR7cHnG5sbAx7n8BOuWdCeSio8w0q8BB8
#58viJiu1S_VTKqmitzn6WnDkaYdcr7WiMrlvAGSzyHY

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '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')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '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')

# Ensure API keys are set
if not OPENAI_API_KEY or OPENAI_API_KEY == '':
    raise ValueError("OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == '':
    raise ValueError("Anthropic API key not set. Please set the ANTHROPIC_API_KEY environment variable.")

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))




@app.route('/cocounsel')
def cocounsel():
    return render_template('cocounsel_index.html')



@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    try:
        data = request.get_json()
        legal_dispute = data.get('dispute', '').strip()
        if not legal_dispute:
            return jsonify({'error': 'No legal dispute provided'}), 400

        # Generate questions using Anthropic API
        questions_text = generate_clarificatory_questions(legal_dispute)

        # Parse questions
        questions = parse_questions(questions_text)

        return jsonify({'questions': questions})

    except Exception as e:
        print(f"Error in generate_questions: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while generating questions.'}), 500




@app.route('/process_dispute', methods=['POST'])
def process_dispute():
    try:
        data = request.get_json()
        factual_dispute = data.get('dispute', '').strip()
        # questions = data.get('questions', [])
        # answers = data.get('answers', [])
        if not factual_dispute:
            return jsonify({'error': 'No factual dispute provided'}), 400

        print(NEO4J_URI)
        print(NEO4J_PASSWORD)


        # Combine the dispute, questions, and answers
        # factual_dispute = factual_dispute + "\n\nClarificatory Questions and Answers:\n"
        # for q, a in zip(questions, answers):
        #     factual_dispute += f"Q: {q}\nA: {a}\n"

        # Step 1: Generate initial memo and parse case names
        initial_memo_response = generate_initial_memo(factual_dispute)
        memo_text, case_names = parse_initial_memo_and_case_names(initial_memo_response)
        
        case_names.append("Aneeta Hada vs M/S Godfather Travels & Tours Private Limited (2012)")

        print("Initial Memo:", memo_text)
        print("Case Names:", case_names)

        # Step 2: Generate embeddings
        dispute_embedding = create_embedding(factual_dispute)

        memo_embedding = create_embedding(memo_text)

        # Step 3: Query Neo4j database
        with driver.session() as session:
            # Search legal issues based on dispute embedding
            legal_issue_ids = session.read_transaction(search_legal_issues, dispute_embedding)

            # Get documents from legal issues
            documents_from_legal_issues = session.read_transaction(get_documents_from_legal_issues, legal_issue_ids)

            # Search documents based on memo embedding
            documents_from_memo = session.read_transaction(search_documents, memo_embedding)

            # Combine document sets
            total_docs = set(documents_from_legal_issues).union(set(documents_from_memo))

            # Get document IDs for the case names
            case_document_ids = session.read_transaction(get_document_ids_by_case_names, case_names)

            # Remove None values from case_document_ids
            case_document_ids = [doc_id for doc_id in case_document_ids if doc_id is not None]

            if not case_document_ids:
                return jsonify({'error': 'No relevant documents found for the provided case names.'}), 404


            # Get related documents of case document IDs
            related_document_ids = session.read_transaction(get_related_documents, case_document_ids)

            # Find intersection of related documents and total docs
            all_document_ids = list(set(related_document_ids).intersection(total_docs))

            # Remove case document IDs from documents to be sent to the Haiku API
            documents_for_haiku = list(set(all_document_ids) - set(case_document_ids))

            if not case_document_ids:
                return jsonify({'error': 'No relevant documents found.'}), 404

        # Set the maximum token limit
        max_token_limit = 195000

        # Initialize a copy of documents_for_haiku to modify
        documents_for_haiku_copy = documents_for_haiku.copy()

        # Loop to ensure the token count is within the limit
        while True:
            with driver.session() as session:
                # Get case law summaries
                case_law_summaries = session.read_transaction(get_case_law_summaries, documents_for_haiku_copy)

            # Prepare case law summaries text
            case_law_summaries_text = format_case_law_summaries(case_law_summaries)

            # Estimate the total token count
            total_token_count = estimate_token_count(factual_dispute + memo_text + case_law_summaries_text)

            if total_token_count <= max_token_limit:
                break
            elif documents_for_haiku_copy:
                # Remove the last document ID
                documents_for_haiku_copy.pop()
            else:
                # If no documents are left, break the loop
                break

        if not documents_for_haiku_copy:
            return jsonify({'error': 'Unable to process due to token limit constraints.'}), 400

        # Use the adjusted documents_for_haiku_copy for further processing
        documents_for_haiku = documents_for_haiku_copy

        # Step 4: Select relevant case laws
        selected_case_laws_text = select_relevant_case_laws(factual_dispute, memo_text, case_law_summaries_text)

        print("Selected Case Laws Text:", selected_case_laws_text)

        # Parse selected case laws to get doc_ids and analysis_reasoning_ids
        selected_case_laws = parse_selected_case_laws(selected_case_laws_text)

        # Add case document IDs directly to selected case laws with all analysis_reasoning_ids
        with driver.session() as session:
            for doc_id in case_document_ids:
                analysis_reasoning_ids = session.read_transaction(
                    get_all_analysis_reasoning_ids_for_document, doc_id
                )
                selected_case_laws.append({
                    'doc_id': doc_id,
                    'analysis_reasoning_ids': analysis_reasoning_ids
                })

        if not selected_case_laws:
            return jsonify({'error': 'No relevant case laws selected.'}), 404

        # Get the paragraphs for the selected analysis reasoning ids
        analysis_reasoning_ids = []
        for case in selected_case_laws:
            analysis_reasoning_ids.extend(case['analysis_reasoning_ids'])

        with driver.session() as session:
            paragraphs = session.read_transaction(get_paragraphs_for_analysis_reasoning, analysis_reasoning_ids)
            # Get case law summaries for all selected case laws (including those added directly)
            all_doc_ids = [case['doc_id'] for case in selected_case_laws]
            case_law_summaries = session.read_transaction(get_case_law_summaries_by_ids, all_doc_ids)
        
        doc_id_to_case_title = {case['document_id']: case['case_title'] for case in case_law_summaries}

        # Prepare data for the final memo
        case_laws_with_paragraphs = merge_case_law_summaries_with_paragraphs(case_law_summaries, paragraphs)

        # Step 5: Generate final research memo
        final_memo = generate_final_memo(factual_dispute, case_laws_with_paragraphs, case_law_summaries)

        print("Final Memo:", final_memo)


        # After generating the final_memo, prepare the initial conversation
        # Initialize conversation with user prompt and assistant memo
        initial_conversation = [
            {
                "role": "user",
                "content": generate_final_memo_prompt(factual_dispute, case_laws_with_paragraphs, case_law_summaries)
            },
            {
                "role": "assistant",
                "content": final_memo  # The memo generated by Claude
            }
        ]

        # Inside the process_dispute function, after selecting case laws
        response = {
            'initial_conversation': initial_conversation,
            'cases': [
                {
                    'doc_id': case['doc_id'],
                    'case_title': doc_id_to_case_title.get(case['doc_id'], ''),
                    'analysis_reasoning_ids': case['analysis_reasoning_ids']
                }
                for case in selected_case_laws
            ],
            'final_memo': final_memo
        }


        return jsonify(response)

    except Exception as e:
        # Log the exception with traceback for debugging
        print(f"Error in process_dispute: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while processing the dispute.'}), 500


        # Prepare response
        response = {
            'initial_memo': memo_text,
            'case_titles': [doc_id_to_case_title.get(case['doc_id'], '') for case in selected_case_laws],
            'final_memo': final_memo
        }

        return jsonify(response)

    except Exception as e:
        # Log the exception with traceback for debugging
        print(f"Error in process_dispute: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while processing the dispute.'}), 500


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        conversation = data.get('conversation', [])
        user_task = data.get('user_task', '').strip()

        if not user_task:
            return jsonify({'error': 'No user task provided'}), 400

        # Append the latest user message to the conversation
        conversation.append({
            "role": "user",
            "content": user_task
        })

        # Ensure the conversation does not exceed 20 user messages
        user_message_count = sum(1 for msg in conversation if msg['role'] == 'user')
        if user_message_count > 20:
            # Remove the oldest user message and corresponding assistant message
            for i, msg in enumerate(conversation):
                if msg['role'] == 'user':
                    del conversation[i]
                    # Also remove the corresponding assistant message if exists
                    if i < len(conversation):
                        del conversation[i]
                    break

        # Construct the messages for the Claude API with proper structure
        messages_for_api = []
        for msg in conversation:
            if msg['role'] in ['user', 'assistant']:
                messages_for_api.append({
                    "role": msg['role'],
                    "content": [
                        {
                            "type": "text",
                            "text": msg['content']
                        }
                    ]
                })

        # Call the Claude API
        assistant_response = call_claude_api(messages_for_api)

        # Append assistant response to the conversation
        conversation.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Return the assistant response along with the updated conversation
        return jsonify({'assistant_response': assistant_response, 'conversation': conversation})

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while processing the chat.'}), 500



@app.route('/get_case_details', methods=['POST'])
def get_case_details():
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        analysis_reasoning_ids = data.get('analysis_reasoning_ids', [])

        if not document_id:
            return jsonify({'error': 'No document ID provided'}), 400

        with driver.session() as session:
            # Fetch case summary
            case_summary = session.read_transaction(get_case_summary, document_id)

            # Fetch case text (paragraphs)
            case_text = session.read_transaction(get_case_text, document_id, analysis_reasoning_ids)

        response = {
            'case_summary': case_summary,
            'case_text': case_text
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error in get_case_details: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while fetching case details.'}), 500
    





def generate_clarificatory_questions(legal_dispute):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""You are an AI legal researcher tasked with preparing for research on a legal dispute. Your goal is to ensure you have a comprehensive understanding of the dispute before proceeding with the research. You will be provided with details of a legal dispute, and your job is to identify any information gaps, areas needing clarification, or additional details required to fully grasp the situation.

Here is the legal dispute you need to analyze:

<legal_dispute>
{legal_dispute}
</legal_dispute>

Carefully read and analyze the provided information. Consider the following aspects:
1. Parties involved
2. Nature of the dispute
3. Relevant dates and timelines
5. Key facts and events
6. Any prior legal proceedings or decisions

If you find any gaps in information, need clarification, or require additional details to fully understand the legal dispute, formulate questions to address these issues. Your questions should be:
- Focused on completing the legal dispute details
- Aimed at enabling a comprehensive understanding of the situation
- Concise and clear
- Relevant to the core issues of the dispute

Do not ask an excessive number of questions. Prioritize the most critical information gaps or areas of ambiguity.

Present your questions in the following format:
<questions>
1. [Your first question here]
2. [Your second question here]
3. [Continue as needed]
</questions>

If you believe you have all the necessary information to proceed with legal research and do not need to ask any questions, state this clearly:
<no_questions>
Based on the provided information, I have a comprehensive understanding of the legal dispute and do not require additional clarification to proceed with legal research.
</no_questions>

Remember:
- Focus on gathering essential information only
- Avoid making assumptions about missing details
- Ensure your questions are directly related to understanding the legal dispute
- If the provided information is sufficient, don't hesitate to state that no further questions are needed

Begin your analysis and formulate your questions or state that you have sufficient information.
"""

        response = client.messages.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=4096,
            model="claude-3-5-sonnet-20241022",
        )
        return ''.join(block.text for block in response.content)
    except Exception as e:
        print(f"Error generating clarificatory questions: {str(e)}")
        raise


def parse_questions(questions_text):
    try:
        # Check if <no_questions> tag is present
        if "<no_questions>" in questions_text:
            return []

        # Extract questions between <questions> tags
        match = re.search(r'<questions>(.*?)</questions>', questions_text, re.DOTALL)
        if not match:
            return []

        questions_block = match.group(1).strip()

        # Extract each question, assuming they are numbered
        questions = re.findall(r'\d+\.\s*(.*)', questions_block)
        return questions
    except Exception as e:
        print(f"Error parsing questions: {str(e)}")
        raise


def create_embedding(text):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            input=text.replace("\\n", "  "),
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise

def generate_initial_memo(factual_dispute):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""You are tasked with formulating a draft reasoned memo on a legal dispute using relevant precedents. Before drafting the memo, you must conduct thorough legal research. Your research should focus on finding relevant case laws, statutes, and legal principles, with a preference for precedents set by the Supreme Court of India. After completing your research, proceed to draft the memo following the structure and guidelines provided below. Your memo should follow a specific structure and adhere to certain parameters for effective legal analysis. Here are the details of the dispute:\n\n<legal_dispute>\n{factual_dispute}\n</legal_dispute>

Your task is to create a well-structured legal memo addressing this dispute. The memo should contain the following sections:\n\n1. Brief facts\n2. Issues involved\n3. Laws involved\n4. Discussion/Reasoning\n5. Findings/Conclusion\n\nFor each section, follow these guidelines:\n\n1. Brief facts:\n   Summarize the key facts of the dispute concisely. Include only the most relevant information necessary for understanding the legal issues at hand.\n\n2. Issues involved:\n   Identify and clearly state the main legal questions or issues that need to be addressed in this dispute. Frame these as specific questions that your memo will answer.\n\n3. Laws involved:\n   List and briefly explain the relevant laws, statutes, or legal principles that apply to this case. Reference specific sections or articles where applicable. For each law, briefly explain how it is pertinent to the issues at hand.\n\n4. Discussion/Reasoning:\n   This should be the most substantial part of your memo. Analyze the facts in light of the relevant laws and precedents. Consider the following:\n   - Explain how the law applies to the specific facts of this case\n   - Discuss any relevant precedents and how they relate to the current dispute\n   - Address potential counterarguments or alternative interpretations\n   - Use logical reasoning to support your analysis\n    \n    Ensure that your memo reads professionally and is appropriate for a legal audience. Provide in-depth reasoning, citing specific facts and legal principles, and explain how they interconnect.\n\n5. Findings/Conclusion:\n   Based on your analysis, provide a clear conclusion for each issue identified. State your opinion on how the dispute should be resolved and why.\n\nThroughout your memo, pay attention to the following parameters:\n\na) Ability to use relevant legal sources: Cite and apply the provided precedents appropriately. Demonstrate how these sources support your reasoning.\n\nb) Use of legal language: Employ proper legal terminology and phrasing throughout your memo. Avoid colloquialisms and use formal language.\n\nc) Exposition of the law: Clearly explain the relevant laws and legal principles. Ensure that your explanation reads professionally and is appropriate for a legal audience.\n\nd) Analysis of the facts and applicability of the law to the facts: Show a clear connection between the facts of the case and the laws you're applying. Explain why certain laws are relevant and how they should be interpreted in this specific context.\n\ne) Structure of the opinion: Follow the outlined structure closely. Use clear headings for each section and ensure a logical flow of ideas throughout the memo.\n\nFormat your response as follows:\n\n<memo>\n<brief_facts>\n[Your content here]\n</brief_facts>\n\n<issues_involved>\n[Your content here]\n</issues_involved>\n\n<laws_involved>\n[Your content here]\n</laws_involved>\n\n<discussion_reasoning>\n[Your content here]\n</discussion_reasoning>\n\n<findings_conclusion>\n[Your content here]\n</findings_conclusion>\n</memo>\n\n. After drafting the memo, please provide a separate section listing all the case laws and precedents you researched and cited in the memo. Prioritize Supreme Court of India judgments, but include other relevant cases if necessary. Format this section as follows:
<researched_cases>

[Case name] [(Year)]
[Case name] [(Year)]
[Continue listing all researched cases]
</researched_cases>Ensure that your memo is well-organized, logically structured, and professionally written. Use paragraph breaks within sections to improve readability. Cite specific laws, precedents, or facts where relevant.

"""

        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return ''.join(block.text for block in response.content)
    except Exception as e:
        print(f"Error generating initial memo: {str(e)}")
        raise


def parse_initial_memo_and_case_names(initial_memo_text):
    try:
        # Extract memo content
        memo_match = re.search(r'<memo>(.*?)</memo>', initial_memo_text, re.DOTALL)
        memo_content = memo_match.group(1).strip() if memo_match else ''

        # Extract case names
        cases_match = re.search(r'<researched_cases>(.*?)</researched_cases>', initial_memo_text, re.DOTALL)
        cases_content = cases_match.group(1).strip() if cases_match else ''
        case_names = re.findall(r'\[Case name\](.*?)\[(Year)\]', cases_content)

        # If the format is different, adjust the regex accordingly
        if not case_names:
            case_names = [case.strip() for case in cases_content.split('\n') if case.strip()]

        return memo_content, case_names
    except Exception as e:
        print(f"Error parsing initial memo and case names: {str(e)}")
        raise


def search_legal_issues(tx, embedding):
    try:
        query = """
        CALL db.index.vector.queryNodes('legal_issues_vector_idx', 200, $embedding) 
        YIELD node, score
        RETURN id(node) AS id
        """
        result = tx.run(query, embedding=embedding)
        return [record['id'] for record in result]
    except Exception as e:
        print(f"Error searching legal issues: {str(e)}")
        raise

def get_documents_from_legal_issues(tx, legal_issue_ids):
    try:
        query = """
        MATCH (li)
        WHERE id(li) IN $legal_issue_ids
        MATCH (li)-[:SUMMARIZES]->(doc:Document)
        RETURN DISTINCT id(doc) AS id
        """
        result = tx.run(query, legal_issue_ids=legal_issue_ids)
        return [record['id'] for record in result]
    except Exception as e:
        print(f"Error getting documents from legal issues: {str(e)}")
        raise

def search_documents(tx, embedding):
    try:
        query = """
        CALL db.index.vector.queryNodes('full_summary_vector_idx', 200, $embedding) 
        YIELD node, score
        RETURN id(node) AS id
        """
        result = tx.run(query, embedding=embedding)
        return [record['id'] for record in result]
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        raise


def get_document_ids_by_case_names(tx, case_names):
    try:
        document_ids = []
        for case_name in case_names:
            # Remove special characters and normalize spaces
            cleaned_case_name = (
                case_name
                .replace('/', '')
                .replace('&', '')
                .replace('(', '')
                .replace(')', '')
                .replace('[', '')
                .replace(']', '')
                .replace('{', '')
                .replace('}', '')
                .replace('\\', '')
                .replace('\'', '')
                .replace('"', '')
                .replace('`', '')
                .replace('@', '')
                .replace('#', '')
                .replace('$', '')
                .replace('%', '')
                .replace('^', '')
                .replace('*', '')
                .replace('+', '')
                .replace('=', '')
                .replace('|', '')
                .replace('<', '')
                .replace('>', '')
                .replace('?', '')
                .replace('!', '')
                .replace(';', '')
                .replace(':', '')
            )
            # Replace multiple spaces with a single space and trim
            cleaned_case_name = ' '.join(cleaned_case_name.split())

            print(cleaned_case_name)
            
            query = """
            CALL db.index.fulltext.queryNodes("doc_case_title", $search_term, {mode: "PHRASE"}) YIELD node, score
            WITH node, score
            ORDER BY score DESC
            LIMIT 1
            RETURN CASE
                WHEN node.full_summary_embedding IS NOT NULL THEN id(node)
                ELSE null
            END AS document_id
            """
            result = tx.run(query, search_term=cleaned_case_name)
            record = result.single()
            # Append the document_id or None if it's null
            document_ids.append(record['document_id'] if record else None)
        return document_ids
    except Exception as e:
        print(f"Error getting document IDs by case names: {str(e)}")
        raise




def get_related_documents(tx, document_ids):
    try:
        query = """
        MATCH (d:Document)
        WHERE id(d) IN $document_ids
        OPTIONAL MATCH (d)-[:CITES]->(cited:Document)
        OPTIONAL MATCH (d)<-[:CITES]-(citing:Document)
        WITH COLLECT(DISTINCT cited) + COLLECT(DISTINCT citing) AS related_docs
        UNWIND related_docs AS doc
        WITH DISTINCT doc
        WHERE doc.full_summary_embedding IS NOT NULL
        RETURN COLLECT(id(doc)) AS related_doc_ids
        """
        result = tx.run(query, document_ids=document_ids)
        record = result.single()
        related_doc_ids = record['related_doc_ids'] if record else []
        return related_doc_ids
    except Exception as e:
        print(f"Error getting related documents: {str(e)}")
        raise

def get_case_law_summaries(tx, document_ids):
    try:
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
            COLLECT(DISTINCT {text: li.final_text, index: coalesce(li.index, 0)}) AS legal_issues,
            COLLECT(DISTINCT {text: arg.final_text, index: coalesce(arg.index, 0)}) AS arguments,
            COLLECT(DISTINCT {text: ar.final_text, index: coalesce(ar.index, 0), id: id(ar)}) AS analysis_reasoning,
            COLLECT(DISTINCT {text: dco.final_text, index: coalesce(dco.index, 0)}) AS dissenting_concurring
        RETURN {
            document_id: id(d),
            case_title: d.case_title,
            background_facts: bf.final_text,
            legal_issues: [issue IN legal_issues WHERE issue.text IS NOT NULL | issue],
            arguments: [arg IN arguments WHERE arg.text IS NOT NULL | arg],
            analysis_reasoning: [ar IN analysis_reasoning WHERE ar.text IS NOT NULL | ar],
            decision_order: do.final_text,
            dissenting_concurring: [dco IN dissenting_concurring WHERE dco.text IS NOT NULL | dco]
        } AS summary
        """
        result = tx.run(query, document_ids=document_ids)
        return [record['summary'] for record in result]
    except Exception as e:
        print(f"Error getting case law summaries: {str(e)}")
        raise


def get_case_law_summaries_by_ids(tx, document_ids):
    try:
        # Similar to get_case_law_summaries but fetches summaries for specific document IDs
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
            COLLECT(DISTINCT {text: li.final_text, index: coalesce(li.index, 0)}) AS legal_issues,
            COLLECT(DISTINCT {text: arg.final_text, index: coalesce(arg.index, 0)}) AS arguments,
            COLLECT(DISTINCT {text: ar.final_text, index: coalesce(ar.index, 0), id: id(ar)}) AS analysis_reasoning,
            COLLECT(DISTINCT {text: dco.final_text, index: coalesce(dco.index, 0)}) AS dissenting_concurring
        RETURN {
            document_id: id(d),
            case_title: d.case_title,
            background_facts: bf.final_text,
            legal_issues: [issue IN legal_issues WHERE issue.text IS NOT NULL | issue],
            arguments: [arg IN arguments WHERE arg.text IS NOT NULL | arg],
            analysis_reasoning: [ar IN analysis_reasoning WHERE ar.text IS NOT NULL | ar],
            decision_order: do.final_text,
            dissenting_concurring: [dco IN dissenting_concurring WHERE dco.text IS NOT NULL | dco]
        } AS summary
        """
        result = tx.run(query, document_ids=document_ids)
        return [record['summary'] for record in result]
    except Exception as e:
        print(f"Error getting case law summaries by IDs: {str(e)}")
        raise



def format_case_law_summaries(case_law_summaries):
    try:
        summaries_text = ''
        for case in case_law_summaries:
            summaries_text += f"<case_law>\n<doc_id>{case['document_id']}</doc_id>\n<case_title>{case['case_title']}</case_title>\n"
            summaries_text += f"<background_facts>\n{case.get('background_facts', '')}\n</background_facts>\n"
            summaries_text += "<legal_issues>\n"
            for issue in case.get('legal_issues', []):
                summaries_text += f"{issue['text']}\n"
            summaries_text += "</legal_issues>\n"
            summaries_text += "<arguments>\n"
            for arg in case.get('arguments', []):
                summaries_text += f"{arg['text']}\n"
            summaries_text += "</arguments>\n"
            summaries_text += "<analysis_reasoning>\n"
            for ar in case.get('analysis_reasoning', []):
                summaries_text += f"<analysis_reasoning_id>{ar['id']}</analysis_reasoning_id>\n"
                summaries_text += f"{ar['text']}\n"
            summaries_text += "</analysis_reasoning>\n"
            summaries_text += f"<decision_order>\n{case.get('decision_order', '')}\n</decision_order>\n"
            summaries_text += "<dissenting_concurring>\n"
            for dc in case.get('dissenting_concurring', []):
                summaries_text += f"{dc['text']}\n"
            summaries_text += "</dissenting_concurring>\n"
            summaries_text += "</case_law>\n"
        return summaries_text
    except Exception as e:
        print(f"Error formatting case law summaries: {str(e)}")
        raise

def select_relevant_case_laws(factual_dispute, initial_memo, case_law_summaries_text):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""You are a skilled legal researcher tasked with identifying relevant case laws based on a factual dispute and an initial research memo. Your goal is to select cases that warrant further research to better understand the legal dispute at hand.


First, carefully read the following legal dispute and initial research memo:

<legal_dispute>
{factual_dispute}
</legal_dispute>

<initial_memo>
{initial_memo}
</initial_memo>

You will now be provided with a long list of case law summaries. Each case law summary has the following structure:
- One unique doc_id for the entire case law
- Multiple sections within each summary
- Analysis and reasoning sections with unique analysis_reasoning_ids

Here are the case law summaries:

<case_law_summaries>
{case_law_summaries_text}
</case_law_summaries>

Analyze each case law summary carefully and select those that are most relevant to the given factual dispute and initial memo. Consider the following factors:
1. Similarity of facts to the given dispute
2. Legal principles discussed
3. Reasoning applied by the court
4. Outcome of the case
5. If the case law is relevant, identify the most relevant analysis_reasoning_ids (usually just one)

Select case laws that you believe should be researched further. For each selected case law:
1. Note the doc_id
2. Identify the most relevant analysis_reasoning_ids (usually just one)

Important guidelines:
- Aim for a comprehensive selection of relevant case laws
- Include cases that offer different perspectives or interpretations
- Consider both supporting and opposing viewpoints
- For each selected case, choose only the most relevant analysis_reasoning_ids (usually just one)

After your analysis, provide your output in the following format:

<selected_case_laws>
<case_law>
<doc_id>[Insert doc_id here]</doc_id>
<relevant_analysis_ids>
<analysis_id>[Insert most relevant analysis_reasoning_id]</analysis_id>
</relevant_analysis_ids>
</case_law>
[Repeat for each selected case law]
</selected_case_laws>

Remember, your selection of case laws should be comprehensive, but the analysis_reasoning_ids for each case should be limited to the most relevant ones. If you're unsure about including a case law, err on the side of inclusion. The goal is to ensure a thorough foundation for further research while focusing on the most pertinent legal reasoning.

"""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0,
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return ''.join(block.text for block in response.content)
    except Exception as e:
        print(f"Error selecting relevant case laws: {str(e)}")
        raise

def parse_selected_case_laws(selected_case_laws_text):
    try:
        selected_case_laws = []
        case_blocks = re.findall(r'<case_law>(.*?)</case_law>', selected_case_laws_text, re.DOTALL)
        for case_block in case_blocks:
            doc_id_match = re.search(r'<doc_id>(\d+)</doc_id>', case_block)
            if not doc_id_match:
                continue
            doc_id = int(doc_id_match.group(1))
            analysis_ids = re.findall(r'<analysis_id>(\d+)</analysis_id>', case_block)
            analysis_ids = [int(aid) for aid in analysis_ids]
            selected_case_laws.append({'doc_id': doc_id, 'analysis_reasoning_ids': analysis_ids})
        return selected_case_laws
    except Exception as e:
        print(f"Error parsing selected case laws: {str(e)}")
        raise


def get_all_analysis_reasoning_ids_for_document(tx, document_id):
    try:
        query = """
        MATCH (d:Document)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
        WHERE id(d) = $document_id
        RETURN id(ar) AS ar_id
        """
        result = tx.run(query, document_id=document_id)
        return [record['ar_id'] for record in result]
    except Exception as e:
        print(f"Error getting analysis reasoning IDs for document: {str(e)}")
        raise


def get_paragraphs_for_analysis_reasoning(tx, analysis_reasoning_ids):
    try:
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
            paragraphs[ar_id].append({'paragraph_number': record['para_num'], 'text': record['text']})
        return paragraphs
    except Exception as e:
        print(f"Error getting paragraphs for analysis reasoning: {str(e)}")
        raise

def merge_case_law_summaries_with_paragraphs(case_law_summaries, paragraphs):
    try:
        for case in case_law_summaries:
            for ar in case.get('analysis_reasoning', []):
                ar_id = ar['id']
                ar['paragraphs'] = paragraphs.get(ar_id, [])
        return case_law_summaries
    except Exception as e:
        print(f"Error merging case law summaries with paragraphs: {str(e)}")
        raise

def generate_final_memo(factual_dispute, case_laws_with_paragraphs, case_law_summaries):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        # Function to prepare case laws text
        def prepare_case_laws_text(case_laws, include_paragraphs=True):
            case_laws_text = ''
            for case in case_laws:
                case_laws_text += f"<{case['case_title']}>\n"
                case_laws_text += f"<background_facts>\n{case.get('background_facts', '')}\n</background_facts>\n"
                case_laws_text += "<legal_issues>\n"
                for issue in case.get('legal_issues', []):
                    case_laws_text += f"{issue['text']}\n"
                case_laws_text += "</legal_issues>\n"
                case_laws_text += "<arguments>\n"
                for arg in case.get('arguments', []):
                    case_laws_text += f"{arg['text']}\n"
                case_laws_text += "</arguments>\n"
                case_laws_text += "<analysis_reasoning>\n"
                for ar in case.get('analysis_reasoning', []):
                    case_laws_text += f"{ar['text']}\n"
                    if include_paragraphs:
                        for para in ar.get('paragraphs', []):
                            case_laws_text += f"{para['text']}\n"
                case_laws_text += "</analysis_reasoning>\n"
                case_laws_text += f"<decision_order>\n{case.get('decision_order', '')}\n</decision_order>\n"
                case_laws_text += "<dissenting_concurring>\n"
                for dc in case.get('dissenting_concurring', []):
                    case_laws_text += f"{dc['text']}\n"
                case_laws_text += "</dissenting_concurring>\n"
                case_laws_text += f"</{case['case_title']}>\n"
            return case_laws_text

        # Prepare case laws text with paragraphs
        case_laws_text_with_paragraphs = prepare_case_laws_text(case_laws_with_paragraphs)
        
        # Check token count
        total_tokens = estimate_token_count(factual_dispute + case_laws_text_with_paragraphs)
        
        # If token count exceeds limit, use summaries without paragraphs
        if total_tokens > 195000:
            case_laws_text = prepare_case_laws_text(case_law_summaries, include_paragraphs=False)
        else:
            case_laws_text = case_laws_text_with_paragraphs

        prompt = f"""You are tasked with formulating a draft reasoned memo on a legal dispute using relevant precedents. Your memo should follow a specific structure and adhere to certain parameters for effective legal analysis. Here are the details of the dispute and precedents:\n\n<relevant_precedents>\n{case_laws_text}\n</relevant_precedents>\n\n<legal_dispute>\n{factual_dispute}\n</legal_dispute>\n\nYour task is to create a well-structured legal memo addressing this dispute. The memo should contain the following sections:\n\n1. Brief facts\n2. Issues involved\n3. Laws involved\n4. Discussion/Reasoning\n5. Findings/Conclusion\n\nFor each section, follow these guidelines:\n\n1. Brief facts:\n   Summarize the key facts of the dispute concisely. Include only the most relevant information necessary for understanding the legal issues at hand.\n\n2. Issues involved:\n   Identify and clearly state the main legal questions or issues that need to be addressed in this dispute. Frame these as specific questions that your memo will answer.\n\n3. Laws involved:\n   List and briefly explain the relevant laws, statutes, or legal principles that apply to this case. Reference specific sections or articles where applicable.\n\n4. Discussion/Reasoning:\n   This should be the most substantial part of your memo. Analyze the facts in light of the relevant laws and precedents. Consider the following:\n   - Explain how the law applies to the specific facts of this case\n   - Discuss any relevant precedents and how they relate to the current dispute\n   - Address potential counterarguments or alternative interpretations\n   - Use logical reasoning to support your analysis\n    \n    Ensure that your memo reads professionally and is appropriate for a legal audience. Provide in-depth reasoning, citing specific facts and legal principles, and explain how they interconnect.\n\n5. Findings/Conclusion:\n   Based on your analysis, provide a clear conclusion for each issue identified. State your opinion on how the dispute should be resolved and why.\n\nThroughout your memo, pay attention to the following parameters:\n\na) Ability to use relevant legal sources: Cite and apply the provided precedents appropriately. Demonstrate how these sources support your reasoning.\n\nb) Use of legal language: Employ proper legal terminology and phrasing throughout your memo. Avoid colloquialisms and use formal language.\n\nc) Exposition of the law: Clearly explain the relevant laws and legal principles. Ensure that your explanation reads professionally and is appropriate for a legal audience.\n\nd) Analysis of the facts and applicability of the law to the facts: Show a clear connection between the facts of the case and the laws you're applying. Explain why certain laws are relevant and how they should be interpreted in this specific context.\n\ne) Structure of the opinion: Follow the outlined structure closely. Use clear headings for each section and ensure a logical flow of ideas throughout the memo.\n\nFormat your response as follows:\n\n<memo>\n<brief_facts>\n[Your content here]\n</brief_facts>\n\n<issues_involved>\n[Your content here]\n</issues_involved>\n\n<laws_involved>\n[Your content here]\n</laws_involved>\n\n<discussion_reasoning>\n[Your content here]\n</discussion_reasoning>\n\n<findings_conclusion>\n[Your content here]\n</findings_conclusion>\n</memo>\n\nEnsure that your memo is well-organized, logically structured, and professionally written. Use paragraph breaks within sections to improve readability. Cite specific laws, precedents, or facts from the provided information where relevant.

"""

        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            temperature=0,
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return ''.join(block.text for block in response.content)
    except Exception as e:
        print(f"Error generating final memo: {str(e)}")
        raise


def generate_final_memo_prompt(factual_dispute, case_laws_with_paragraphs, case_law_summaries):
    # Function to prepare case laws text
    def prepare_case_laws_text(case_laws, include_paragraphs=True):
        case_laws_text = ''
        for case in case_laws:
            case_laws_text += f"<{case['case_title']}>\n"
            case_laws_text += f"<background_facts>\n{case.get('background_facts', '')}\n</background_facts>\n"
            case_laws_text += "<legal_issues>\n"
            for issue in case.get('legal_issues', []):
                case_laws_text += f"{issue['text']}\n"
            case_laws_text += "</legal_issues>\n"
            case_laws_text += "<arguments>\n"
            for arg in case.get('arguments', []):
                case_laws_text += f"{arg['text']}\n"
            case_laws_text += "</arguments>\n"
            case_laws_text += "<analysis_reasoning>\n"
            for ar in case.get('analysis_reasoning', []):
                case_laws_text += f"{ar['text']}\n"
                if include_paragraphs:
                    for para in ar.get('paragraphs', []):
                        case_laws_text += f"{para['text']}\n"
            case_laws_text += "</analysis_reasoning>\n"
            case_laws_text += f"<decision_order>\n{case.get('decision_order', '')}\n</decision_order>\n"
            case_laws_text += "<dissenting_concurring>\n"
            for dc in case.get('dissenting_concurring', []):
                case_laws_text += f"{dc['text']}\n"
            case_laws_text += "</dissenting_concurring>\n"
            case_laws_text += f"</{case['case_title']}>\n"
        return case_laws_text

    # Prepare case laws text with paragraphs
    case_laws_text_with_paragraphs = prepare_case_laws_text(case_laws_with_paragraphs)
        
    # Check token count
    total_tokens = estimate_token_count(factual_dispute + case_laws_text_with_paragraphs)
        
    # If token count exceeds limit, use summaries without paragraphs
    if total_tokens > 195000:
        case_laws_text = prepare_case_laws_text(case_law_summaries, include_paragraphs=False)
    else:
        case_laws_text = case_laws_text_with_paragraphs

    prompt = f"""You are tasked with formulating a draft reasoned memo on a legal dispute using relevant precedents. Your memo should follow a specific structure and adhere to certain parameters for effective legal analysis. Here are the details of the dispute and precedents:

<legal_dispute>
{factual_dispute}
</legal_dispute>

<relevant_precedents>
{case_laws_text}
</relevant_precedents>

Your task is to create a well-structured legal memo addressing this dispute. The memo should contain the following sections:

1. Brief facts
2. Issues involved
3. Laws involved
4. Discussion/Reasoning
5. Findings/Conclusion

For each section, follow these guidelines:

1. Brief facts:
   Summarize the key facts of the dispute concisely. Include only the most relevant information necessary for understanding the legal issues at hand.

2. Issues involved:
   Identify and clearly state the main legal questions or issues that need to be addressed in this dispute. Frame these as specific questions that your memo will answer.

3. Laws involved:
   List and briefly explain the relevant laws, statutes, or legal principles that apply to this case. Reference specific sections or articles where applicable. For each law, briefly explain how it is pertinent to the issues at hand.

4. Discussion/Reasoning:
   This should be the most substantial part of your memo. Analyze the facts in light of the relevant laws and precedents. Consider the following:
   - Explain how the law applies to the specific facts of this case
   - Discuss any relevant precedents and how they relate to the current dispute
   - Address potential counterarguments or alternative interpretations
   - Use logical reasoning to support your analysis
   
   Ensure that your memo reads professionally and is appropriate for a legal audience. Provide in-depth reasoning, citing specific facts and legal principles, and explain how they interconnect.

5. Findings/Conclusion:
   Based on your analysis, provide a clear conclusion for each issue identified. State your opinion on how the dispute should be resolved and why.

Throughout your memo, pay attention to the following parameters:

a) Ability to use relevant legal sources: Cite and apply the provided precedents appropriately. Demonstrate how these sources support your reasoning.

b) Use of legal language: Employ proper legal terminology and phrasing throughout your memo. Avoid colloquialisms and use formal language.

c) Exposition of the law: Clearly explain the relevant laws and legal principles. Ensure that your explanation reads professionally and is appropriate for a legal audience.

d) Analysis of the facts and applicability of the law to the facts: Show a clear connection between the facts of the case and the laws you're applying. Explain why certain laws are relevant and how they should be interpreted in this specific context.

e) Structure of the opinion: Follow the outlined structure closely. Use clear headings for each section and ensure a logical flow of ideas throughout the memo.

Format your response as follows:

<memo>
<brief_facts>
[Your content here]
</brief_facts>

<issues_involved>
[Your content here]
</issues_involved>

<laws_involved>
[Your content here]
</laws_involved>

<discussion_reasoning>
[Your content here]
</discussion_reasoning>

<findings_conclusion>
[Your content here]
</findings_conclusion>
</memo>

Ensure that your memo is well-organized, logically structured, and professionally written. Use paragraph breaks within sections to improve readability. Cite specific laws, precedents, or facts from the provided information where relevant.
"""
    return prompt

def call_claude_api(messages):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=messages,
            max_tokens=4096,
            temperature=0,
        )

        # Assuming response['content'] is a list of dicts with 'type' and 'text'
        assistant_reply = ''.join(block.text for block in response.content)

        return assistant_reply

    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        raise



def get_case_summary(tx, document_id):
    try:
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
            COLLECT(DISTINCT {text: li.final_text, index: coalesce(li.index, 0)}) AS legal_issues,
            COLLECT(DISTINCT {text: arg.final_text, index: coalesce(arg.index, 0)}) AS arguments,
            COLLECT(DISTINCT {text: ar.final_text, index: coalesce(ar.index, 0), id: id(ar)}) AS analysis_reasoning,
            COLLECT(DISTINCT {text: dco.final_text, index: coalesce(dco.index, 0)}) AS dissenting_concurring
        RETURN {
            case_title: d.case_title,
            background_facts: bf.final_text,
            legal_issues: [issue IN legal_issues WHERE issue.text IS NOT NULL | issue],
            arguments: [arg IN arguments WHERE arg.text IS NOT NULL | arg],
            analysis_reasoning: [ar IN analysis_reasoning WHERE ar.text IS NOT NULL | ar],
            decision_order: do.final_text,
            dissenting_concurring: [dco IN dissenting_concurring WHERE dco.text IS NOT NULL | dco]
        } AS summary
        """
        result = tx.run(query, document_id=document_id)
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
            else:
                case_text += f"<p>{para_num}. {text}</p>\n"
        return case_text
    except Exception as e:
        print(f"Error getting case text: {str(e)}")
        raise




def estimate_token_count(text):
    # Estimate token count by assuming 4 characters per token
    return int(len(text) / 4)

if __name__ == '__main__':
    app.run(debug=True)
