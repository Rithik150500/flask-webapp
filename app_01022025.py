import os
from flask import Flask, render_template, request
import google.generativeai as genai
import markdown
import re

app = Flask(__name__)

# 1) Configure your PaLM API key:
genai.configure(api_key="AIzaSyDpNgSvW0LIdfTqD4WLSbsMqCIRG5-kkIQ")

def preprocess_markdown(md_text: str) -> str:
    """
    Preprocess Markdown:
    1. Ensure blockquotes (`>`) have a newline before them.
    2. Replace unordered lists (`-`) with paragraphs.
    """
    # 1. Ensure blockquotes (`>`) have a newline before them
    md_text = re.sub(r'(?<!\n)>', r'\n>', md_text)

    # 2. Wrap blockquote text in double quotes.
    # This regex matches a blockquote line: a '>' optionally followed by whitespace,
    # and then captures the rest of the line.
    # It then replaces the line with the same blockquote marker followed by a space,
    # an opening double quote, the captured text, and a closing double quote.
    md_text = re.sub(r'^(>\s*)(.+)$', r'\1"\2"', md_text, flags=re.MULTILINE)

   #  # 2. Convert ordered lists to unordered lists.
   #  # This regex finds lines starting with optional whitespace, followed by one or more digits, a dot, and a space.
   #  # It then replaces that part with the same indentation followed by '- '.
   #  md_text = re.sub(r'^(\s*)\d+\.\s', r'\1- ', md_text, flags=re.MULTILINE)

    # # 2. Replace unordered lists (`-`) with paragraphs
    # md_text = re.sub(r'^\s*-\s*(.*)', r'\n<p>\1</p>', md_text, flags=re.MULTILINE)

    return md_text

# 2) Set up your generation config:
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
   #  "response_mime_type": "text/plain",
}

# 3) Create a model instance (replace with your correct model name if needed):
#    - If you only have access to text-bison-001, use that.
#    - If you have access to gemini-exp-1206, you can use that instead.
abstractive_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# 4) Our prompt template for the abstractive summary:
ABSTRACTIVE_PROMPT_TEMPLATE = """
You are an experienced legal analyst tasked with summarizing a court judgment for other legal professionals. Your goal is to provide a clear, accurate, and comprehensive summary that captures all key aspects of the judgment.

Here is the text of the court judgment you need to analyze:

<judgment>
{judgment_text}
</judgment>

Please carefully read and analyze the entire judgment. Pay special attention to the court's observations and reasoning. Then, use the following process to create your summary:

Provide a comprehensive summary of the judgment using the following structure, ensuring all content is properly formatted in Markdown:

Title of the Case
   - Include the exact name of the parties
   - Provide the citation (if available) and case number

Court and Coram
   - State the name of the court
   - List the judges or justices who delivered or concurred in the judgment

Date of Decision
   - Provide the date on which the final decision was delivered

Key Legal Propositions 
   - Enumerate the principal legal rulings that emerge from the judgment, quoting relevant passages from the judgment, using blockquotes

Facts of the Case
   - Provide a clear overview of the underlying facts
   - Highlight essential background details that led to the dispute or charges

Issues Before the Court 
   - identify and quote the specific parts of the judgment that state or imply the issues, using blockquotes
   - Clearly set out the main legal or factual questions that the court was required to decide

Arguments of the Parties 
   - Summarize the primary submissions or contentions made by each side (the appellant/petitioner and the respondent/defendant)
   - Note any significant procedural objections or jurisdictional points

Analysis / Observations by the Court 
   - Provide a detailed and extensive analysis of the court's reasoning
   - Create subsections for each major point or issue, using subheadings
   - Cite relevant quotes from the judgment, using blockquotes
   - Consider how the court's observations relate to the issues at hand and the arguments presented by the parties
   - Focus on how the court addressed each issue, citing relevant statutes, precedent cases, or interpretive principles
   - Highlight any novel legal interpretations or applications of existing law.
   - If the court relied on specific authorities, mention them and note what principle or ratio was drawn from each cited precedent
   - Where the court interprets statutes or constitutional provisions, highlight the method of interpretation
   - Discuss any significant legal principles established or reaffirmed by the court
   - Address any dissenting opinions or concurrences, if present

Decision 
   - State the final outcome
   - Mention the operative part of the order

Important guidelines
- Focus on accurately capturing the key details and reasoning without adding extraneous commentary.
- Do not invent facts. Rely solely on the content provided in the text of the judgment (or any reliable references clearly incorporated into the text).
- Ensure your summary is comprehensive, focusing on the crucial aspects of the judgment that would be relevant to other legal professionals.
- Pay particular attention to making the "Analysis / Observations by the Court" section as comprehensive and extensive as possible, with clear subsections, as this is a key area of interest for the readers of your summary.
- Format your entire output in Markdown, using appropriate headers, lists, and blockquotes for quotations.

Here's an example of how your output should be structured (note that this is a generic structure and should be filled with the actual content from your analysis):

**[Case name and citation]**

**[Court name and judges]**

**[Decision date]**

**Key Legal Propositions**
[First key proposition(quote relevant passage from the judgment, using blockquotes)] 
[Second key proposition(quote relevant passage from the judgment, using blockquotes)] 
...

**Facts of the Case**
[Overview of facts] 

**Issues Before the Court**
[First issue(quote relevant passage from the judgment, using blockquotes)] 
[Second issue(quote relevant passage from the judgment, using blockquotes)] 
...

**Arguments of the Parties**
**Appellant/Petitioner**
[First argument] 
[Second argument]
...

**Respondent/Defendant**
[First argument] 
[Second argument]
...

**Analysis / Observations by the Court**
[Detailed and extensive analysis of the court's reasoning, addressing each issue and citing relevant authorities. Quote relevant passages from the judgment, using blockquotes)] 

**Decision**
[Final outcome and operative part of the order] 

Please proceed with your analysis and summary of the judgment. Compile your final summary in Markdown format.
"""

def generate_abstractive_summary(judgment_text: str) -> str:
    """Generate an abstractive summary using the provided prompt template."""
    # 1) Create the full prompt
    prompt = ABSTRACTIVE_PROMPT_TEMPLATE.format(judgment_text=judgment_text)
    
    # 2) Start a chat session
    chat_session = abstractive_model.start_chat(history=[])
    
    # 3) Send the message
    response = chat_session.send_message(prompt)

    print(response.text)
    
    # 4) Return the raw text from the API
    return response.text

@app.route("/", methods=["GET", "POST"])
def index():
    summary_html = ""
    user_input_text = ""

    if request.method == "POST":
        # 1) Get the user input from the form
        user_input_text = request.form.get("judgment", "").strip()

        if user_input_text:
            # 2) Generate the abstractive summary
            raw_summary = generate_abstractive_summary(user_input_text)

            # 3) Preprocess the raw Markdown
            processed_md = preprocess_markdown(raw_summary)

            # 4) Convert from processed Markdown to HTML
            summary_html = markdown.markdown(processed_md)
            print(summary_html)

    return render_template("01022025index.html", summary_html=summary_html, input_text=user_input_text)

if __name__ == "__main__":
    # Run the app in debug mode (not recommended for production)
    app.run(debug=True, port=5000)
