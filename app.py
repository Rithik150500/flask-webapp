from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from neo4j import GraphDatabase
import cohere

app = Flask(__name__)

# Neo4j connection details
URI = "neo4j+s://5c45d75b.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "z_pmebMhDaH78lqd5lk_R3ye3TwjAmyaL6YxwUxLe9A"  # Replace with your actual password

# URI = "bolt://localhost:7687"
# USERNAME = "neo4j"
# PASSWORD = "sc_graph_db"

cohere_key = "RwOE11YO4Nql7aTHhOSROenzQVcuvY8WUoLZPdvb"
cohere_client = cohere.Client(cohere_key)

def create_embedding(text):
    OpenAI_API_KEY = "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"
    client = OpenAI(api_key=OpenAI_API_KEY)
    response = client.embeddings.create(
        input=text.replace("\\n", "  "),
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def search_legal_issues(tx, embedding):
    query = """
    CALL db.index.vector.queryNodes('legal_issues_vector_idx', 10, $embedding)
    YIELD node, score
    WHERE node:Legal_issues
    MATCH (node)-[:SUMMARIZES]->(doc:Document)
    OPTIONAL MATCH (doc)<-[:SUMMARIZES]-(bf:Background_facts)
    RETURN node, score, bf.final_text AS background_facts
    ORDER BY score DESC
    LIMIT 10
    """
    return [{"id": record["node"].id, "text": record["node"]["final_text"], "score": record["score"], "background_facts": record["background_facts"]} for record in tx.run(query, embedding=embedding)]


def get_related_documents_good(tx, legal_issue_ids):
    query = """
    MATCH (li:Legal_issues)
    WHERE id(li) IN $legal_issue_ids
    MATCH (li)-[:SUMMARIZES]->(doc:Document)
    WITH COLLECT(DISTINCT doc) AS docs
    UNWIND docs AS main_doc
    OPTIONAL MATCH (main_doc)-[:CITES]->(cited_doc:Document)
    RETURN COLLECT(DISTINCT id(main_doc)) + COLLECT(DISTINCT id(cited_doc)) AS all_doc_ids
    """
    result = tx.run(query, legal_issue_ids=legal_issue_ids)
    return result.single()["all_doc_ids"]

def get_related_documents_bad(tx, legal_issue_ids):
    query = """
    MATCH (li:Legal_issues)
    WHERE id(li) IN $legal_issue_ids
    MATCH (li)-[:SUMMARIZES]->(doc:Document)
    RETURN COLLECT(DISTINCT id(doc)) AS all_doc_ids
    """
    result = tx.run(query, legal_issue_ids=legal_issue_ids)
    return result.single()["all_doc_ids"]

def get_analysis_reasoning(tx, document_ids):
    query = """
    MATCH (doc:Document)
    WHERE id(doc) IN $document_ids
    MATCH (doc)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
    RETURN COLLECT(DISTINCT {
        ar: {id: id(ar), text: ar.final_text},
        doc: {id: id(doc), title: doc.case_title},
        cited_docs: [(ar)-[:SUMMARY_CITES]->(cited:Document) | {id: id(cited), title: cited.case_title}]
    }) AS probable_answer_nodes
    """
    result = tx.run(query, document_ids=document_ids)
    return result.single()["probable_answer_nodes"]

def get_case_summary(tx, document_id, analysis_reasoning_id):
    query = """
    MATCH (d:Document) WHERE id(d) = $document_id
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(bf:Background_facts)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(li:Legal_issues)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(arg:Arguments)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(do:Decision_order)
    OPTIONAL MATCH (d)<-[:SUMMARIZES]-(dco:Dissenting_concurring_opinions)
    WITH d, bf, do,
        COLLECT(DISTINCT {text: li.final_text, index: coalesce(li.index, 0)}) AS legal_issues,
        COLLECT(DISTINCT {text: arg.final_text, index: coalesce(arg.index, 0)}) AS arguments,
        COLLECT(DISTINCT {id: id(ar), text: ar.final_text, index: coalesce(ar.index, 0)}) AS analysis_reasoning,
        COLLECT(DISTINCT {text: dco.final_text, index: coalesce(dco.index, 0)}) AS dissenting_concurring
    RETURN {
        background_facts: bf.final_text,
        legal_issues: [issue IN legal_issues WHERE issue.text IS NOT NULL | issue.text],
        arguments: [arg IN arguments WHERE arg.text IS NOT NULL | arg.text],
        analysis_reasoning: [ar IN analysis_reasoning WHERE ar.text IS NOT NULL | {text: ar.text, id: ar.id, highlight: ar.id = $analysis_reasoning_id}],
        decision_order: do.final_text,
        dissenting_concurring: [dco IN dissenting_concurring WHERE dco.text IS NOT NULL | dco.text]
    } AS summary
    """
    result = tx.run(query, document_id=document_id, analysis_reasoning_id=analysis_reasoning_id)
    return result.single()["summary"]

def get_case_text(tx, document_id, analysis_reasoning_id):
    query = """
    MATCH (d:Document)-[:HAS_PARAGRAPH]->(p:Paragraph)
    WHERE id(d) = $document_id
    OPTIONAL MATCH (ar:Analysis_reasoning)-[:PARA_REF]->(p)
    WHERE id(ar) = $analysis_reasoning_id
    RETURN p.paragraph_text AS text, p.paragraph_number AS number,
           CASE WHEN ar IS NOT NULL THEN true ELSE false END AS highlight
    ORDER BY p.paragraph_number
    """
    result = tx.run(query, document_id=document_id, analysis_reasoning_id=analysis_reasoning_id)
    return [{"text": record["text"], "number": record["number"], "highlight": record["highlight"]} for record in result]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('query', '')

    if not search_query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        # Create embedding
        embedding = create_embedding(search_query)

        # Connect to Neo4j and perform search
        with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
            with driver.session() as session:
                # Get top 10 similar legal issues
                legal_issues = session.execute_read(search_legal_issues, embedding)

        return jsonify(legal_issues)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rate_issue', methods=['POST'])
def rate_issue():
    issue_id = request.form.get('issue_id')
    rating = request.form.get('rating')

    if not issue_id or not rating:
        return jsonify({"error": "Missing issue_id or rating"}), 400

    try:
        issue_id = int(issue_id)
        rating = int(rating)
        if rating not in [-1, 1]:
            raise ValueError("Rating must be -1 or 1")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Here you would typically store the rating in a database
    # For this example, we'll just return a success message
    return jsonify({"success": True})

@app.route('/research', methods=['POST'])
def research():
    good_issues = request.json.get('good_issues', [])
    bad_issues = request.json.get('bad_issues', [])
    search_query = request.json.get('query', '')

    if not good_issues:
        return jsonify({"error": "No positively rated issues provided"}), 400

    try:
        with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
            with driver.session() as session:
                good_docs = session.execute_read(get_related_documents_good, good_issues)
                bad_docs = session.execute_read(get_related_documents_bad, bad_issues)

                all_docs = list(set(good_docs) - set(bad_docs))
                all_doc_ids = [doc for doc in all_docs]

                probable_answers = session.execute_read(get_analysis_reasoning, all_doc_ids)

        # Prepare documents for Cohere reranking
        documents = [node["ar"]["text"] for node in probable_answers]

        # Perform Cohere reranking
        reranked_results = cohere_client.rerank(
            model="rerank-english-v3.0",
            query=search_query,
            documents=documents,
            top_n=len(good_issues + bad_issues)
        )

        # Prepare results for JSON response
        results = []
        for result in reranked_results.results:
            node = probable_answers[result.index]
            results.append({
                'relevance_score': result.relevance_score,
                'text': node["ar"]["text"],
                'case_title': node["doc"]["title"],
                'document_id': node["doc"]["id"],
                'analysis_reasoning_id': node["ar"]["id"],  # Add this line
                'cited_docs': node["cited_docs"]
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/case_details/<int:document_id>/<int:analysis_reasoning_id>', methods=['GET'])
def case_details(document_id, analysis_reasoning_id):
    try:
        with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
            with driver.session() as session:
                summary = session.execute_read(get_case_summary, document_id, analysis_reasoning_id)
                text = session.execute_read(get_case_text, document_id, analysis_reasoning_id)

        return jsonify({"summary": summary, "text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    search_query = request.json.get('query', '')
    cases = request.json.get('cases', [])

    if not search_query or not cases:
        return jsonify({"error": "Missing search query or cases"}), 400

    try:
        # Prepare the prompt
        prompt = f"""
        You are a highly skilled legal analyst tasked with preparing a comprehensive legal analysis in about 4000 words. Your goal is to analyze a given legal issue, considering the facts and relevant Supreme Court judgments. Follow these instructions carefully to produce a well-structured, insightful legal discussion.

        First, review the following information:
        <legal_issue>
        {search_query}
        </legal_issue>

        <relevant_judgments>
        {cases}
        </relevant_judgments>
        Now, prepare your legal memo using the following structure:

        Question Presented
        Craft a concise, one-sentence statement that defines how the law applies to the legal issue at hand. Ensure your question is specific, impartial, and does not assume a legal conclusion.
        Discussion (in atleast 2000 words)
        In this section, showcase your critical legal thinking skills. Organize your analysis into several paragraphs, using subsections based on the legal topics addressed. For each subsection:

        a) Clearly state the relevant law and facts using active voice.
        b) Analyze the facts under the applicable law.
        c) Provide a critical assessment of how the court may apply the law to the matter.
        d) Present your analysis in a logical, step-by-step manner.
        e) Investigate and analyze the legal issue thoroughly, considering all angles.
        Use the provided relevant Supreme Court judgments to support your analysis. When referencing a judgment, briefly explain its relevance to the current case.

        Conclusion (in about 500 words)
        In this final section:
        a) Impartially assess the potential outcome of the matter.
        b) Identify any risks or unknown facts that require further investigation.
        c) Predict how the court will likely apply the law to this case.
        d) Indicate your level of confidence in your prediction based on the available data.
        e) Propose next steps and a legal strategy to proceed, maintaining an impartial advisory tone.

        Throughout your memo, maintain an impartial tone with no implied preference for either side. Use clear, concise language and avoid unnecessary legal jargon. Remember that your audience consists of senior advocates who are already familiar with general law, so focus on case-specific analysis rather than explaining basic legal concepts.
        Present your entire legal memo within <legal_memo> tags. Use appropriate subsection tags for each part of your memo (e.g., <question_presented>, <discussion>, <conclusion>). Within the discussion section, use <subsection> tags to delineate different topics of analysis.
        """

       
        # Use OpenAI API to generate the analysis
        client = OpenAI(api_key="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")
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        response_data = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_data.append({"choices": [{"delta": {"content": chunk.choices[0].delta.content}}]})

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)