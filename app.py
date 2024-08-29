from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from neo4j import GraphDatabase
import cohere
import os


app = Flask(__name__)


URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
PASSWORD = os.environ.get('NEO4J_PASSWORD', 'your_password')
cohere_key = os.environ.get('COHERE_KEY', 'your_cohere_key')
cohere_client = cohere.Client(cohere_key)

def create_embedding(text):
    OpenAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your_openai_key')
    client = OpenAI(api_key=OpenAI_API_KEY)    
    response = client.embeddings.create(
        input=text.replace("\\n", "  "),
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def search_legal_issues(tx, embedding, limit):
    query = """
    CALL db.index.vector.queryNodes('legal_issues_vector_idx', $limit, $embedding)
    YIELD node, score
    WHERE node:Legal_issues
    RETURN node, score
    ORDER BY score DESC
    LIMIT $limit
    """
    return list(tx.run(query, embedding=embedding, limit=limit))

def get_related_nodes(tx, legal_issue_ids):
    query = """
    MATCH (li:Legal_issues)
    WHERE id(li) IN $legal_issue_ids
    MATCH (li)-[:SUMMARIZES]->(doc:Document)
    WITH COLLECT(DISTINCT doc) AS main_docs
    UNWIND main_docs AS main_doc
    OPTIONAL MATCH (main_doc)-[:CITES]->(cited_doc:Document)
    WITH main_docs, COLLECT(DISTINCT cited_doc) AS cited_docs
    UNWIND main_docs + cited_docs AS all_docs
    MATCH (all_docs)<-[:SUMMARIZES]-(ar:Analysis_reasoning)
    RETURN COLLECT(DISTINCT ar) AS probable_answer_nodes
    """
    result = tx.run(query, legal_issue_ids=legal_issue_ids)
    return result.single()["probable_answer_nodes"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('query', '')
    num_results = request.form.get('numResults', '5')  # Default to 5 if not provided

    if not search_query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        num_results = int(num_results)
    except ValueError:
        return jsonify({"error": "Invalid number of results"}), 400

    try:
        # Create embedding
        embedding = create_embedding(search_query)

        # Connect to Neo4j and perform search
        with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
            with driver.session() as session:
                # Get top similar legal issues
                legal_issues = session.execute_read(search_legal_issues, embedding, num_results)
                legal_issue_ids = [issue["node"].id for issue in legal_issues]
                probable_answers = session.execute_read(get_related_nodes, legal_issue_ids)

        # Prepare documents for Cohere reranking
        documents = [node["final_text"] for node in probable_answers]

        # Perform Cohere reranking
        reranked_results = cohere_client.rerank(
            model="rerank-english-v3.0",
            query=search_query,
            documents=documents,
            top_n=num_results
        )

        # Prepare results for JSON response
        results = []
        for i, result in enumerate(reranked_results.results, 1):
            results.append({
                'rank': i,
                'relevance_score': result.relevance_score,
                'text': documents[result.index].replace("\\n", "    ")
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))