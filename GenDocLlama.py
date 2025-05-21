import os
import tempfile
from pathlib import Path
from docx import Document
import PyPDF2
from llama_cpp import Llama
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st

# Initialize LLaMA model (assumes you have the .gguf model file locally)
MODEL_PATH = "./models/llama-2-7b.Q4_K_M.gguf"
llm = Llama(model_path=MODEL_PATH, n_ctx=2048)

# Utility: extract text from Word file
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Utility: extract text from PDF file
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# Utility: extract text from email (.eml)
def extract_text_from_eml(file):
    content = file.read().decode("utf-8")
    return content

# Utility: read code files
SUPPORTED_CODE_EXTENSIONS = ['.py', '.js', '.java', '.cpp', '.ts', '.html', '.css']
def extract_code(file):
    return file.read().decode("utf-8")

# Generate documentation using LLaMA
def generate_documentation_llama(prompt):
    response = llm(
        f"You are a senior technical writer. Create comprehensive technical documentation based on the following project input:\n\n{prompt}",
        max_tokens=1500,
        stop=["</s>"]
    )
    return response["choices"][0]["text"].strip()

# Generate a styled PDF from the generated content
def create_pdf_from_text(text, filename):
    buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(buffer.name, pagesize=letter)
    width, height = letter
    text_obj = c.beginText(40, height - 40)
    text_obj.setFont("Helvetica", 12)

    for line in text.split('\n'):
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.save()
    return buffer.name

# Streamlit UI
st.title("🧠 AI Documentation Generator (Local LLaMA)")

project_description = st.text_area("Project Description (2-3 sentences):")

req_file = st.file_uploader("Upload Requirement Document (PDF or Word)", type=["pdf", "docx"])
code_files = st.file_uploader("Upload Code Files", type=SUPPORTED_CODE_EXTENSIONS, accept_multiple_files=True)
template_file = st.file_uploader("Upload Optional Documentation Template", type=["txt", "md", "docx", "pdf"])
email_thread = st.file_uploader("Upload Related Email Thread (.eml)", type=["eml"])

if st.button("Generate Documentation"):
    full_prompt = project_description + "\n\n"

    # Requirement doc
    if req_file:
        if req_file.name.endswith(".docx"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(req_file.read())
                tmp.flush()
                full_prompt += extract_text_from_docx(tmp.name) + "\n"
        elif req_file.name.endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(req_file.read())
                tmp.flush()
                full_prompt += extract_text_from_pdf(tmp.name) + "\n"

    # Code files
    for file in code_files or []:
        full_prompt += f"\n# File: {file.name}\n"
        full_prompt += extract_code(file)

    # Email
    if email_thread:
        full_prompt += "\n# Email Thread\n"
        full_prompt += extract_text_from_eml(email_thread)

    # Template
    if template_file:
        full_prompt += "\n# Template\n"
        full_prompt += extract_code(template_file)

    # Generate doc
    with st.spinner("Generating documentation using LLaMA..."):
        doc_text = generate_documentation_llama(full_prompt)
        pdf_path = create_pdf_from_text(doc_text, "generated_documentation.pdf")
        st.success("Documentation generated!")
        st.download_button("📥 Download PDF", open(pdf_path, "rb"), file_name="generated_documentation.pdf")
