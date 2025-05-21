import os
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")
import docx
import PyPDF2
from pathlib import Path
from typing import List, Optional
from email import policy
from email.parser import BytesParser
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors

  # Replace with your actual API key

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_eml(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    return msg.get_body(preferencelist=('plain')).get_content()

def read_code_files(file_paths: List[str]) -> str:
    code_content = ""
    for file in file_paths:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            code_content += f"\n\n# File: {file}\n" + f.read()
    return code_content

def call_openai(prompt: str) -> str:
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.5)
    return response.choices[0].message.content

def parse_sections(documentation_text: str):
    """
    Splits documentation into sections based on headings.
    Assumes AI generates sections with titles like '## Project Overview' or 'Project Overview:'
    """
    lines = documentation_text.split('\n')
    sections = []
    current_title = "Introduction"
    current_content = []

    for line in lines:
        if line.strip() and (
            line.strip().endswith(':') or
            line.strip().lower().startswith("project ") or
            line.strip().lower().startswith("requirements") or
            line.strip().lower().startswith("communication")
        ):
            if current_content:
                sections.append((current_title.strip(':').strip(), '\n'.join(current_content).strip()))
                current_content = []
            current_title = line.strip()
        else:
            current_content.append(line)

    if current_content:
        sections.append((current_title.strip(':').strip(), '\n'.join(current_content).strip()))

    return sections

def write_to_pdf_with_toc(sections, output_path: str):
    width, height = LETTER
    margin = 50
    line_height = 14
    font = "Helvetica"
    font_size = 11
    title_font_size = 14
    toc_title_size = 16

    c = canvas.Canvas(output_path, pagesize=LETTER)
    toc_entries = []
    page_number = 1

    def draw_wrapped_text(text, font_name, font_size, max_width, start_y):
        c.setFont(font_name, font_size)
        y = start_y
        for line in text.split('\n'):
            wrapped = simpleSplit(line, font_name, font_size, max_width)
            for subline in wrapped:
                if y <= margin:
                    c.showPage()
                    toc_entries.append(("__PAGE_BREAK__", None))
                    y = height - margin
                    c.setFont(font_name, font_size)
                c.drawString(margin, y, subline)
                y -= line_height
        return y

    # Table of Contents Page
    c.setFont("Helvetica-Bold", toc_title_size)
    c.drawString(margin, height - margin, "Table of Contents")
    y = height - margin - 30

    for i, (title, _) in enumerate(sections):
        toc_entries.append((title, page_number))
        c.setFont("Helvetica", font_size)
        c.drawString(margin, y, f"{i+1}. {title} ..................................... {page_number}")
        y -= line_height
        if y < margin:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica-Bold", toc_title_size)
            c.drawString(margin, y, "Table of Contents (cont'd)")
            y -= line_height * 2

    c.showPage()

    # Content Pages
    for title, content in sections:
        c.setFont("Helvetica-Bold", title_font_size)
        c.drawString(margin, height - margin, title)
        y = height - margin - 20

        y = draw_wrapped_text(content, font, font_size, width - 2 * margin, y)
        c.showPage()
        page_number += 1

    c.save()

def generate_documentation(
    project_description: str,
    req_files: List[str],
    code_files: List[str],
    email_files: List[str],
    output_pdf_path: str
):
    # Extract content
    requirements = "\n".join(
        extract_text_from_pdf(f) if f.endswith('.pdf') else extract_text_from_docx(f)
        for f in req_files
    )
    code = read_code_files(code_files)
    emails = "\n".join(extract_text_from_eml(f) for f in email_files)

    # Prompt
    prompt = (
        f"Project Description:\n{project_description}\n\n"
        f"Requirements:\n{requirements[:4000]}\n\n"
        f"Code Snippets:\n{code[:4000]}\n\n"
        f"Email Summary:\n{emails[:4000]}\n\n"
        "Generate a professional and detailed project documentation in paragraph form. "
        "Include clearly separated sections like Project Overview, Requirements, Code Summary, Communication Summary, and Additional Notes. "
        "Format section titles clearly so they can be used as headers. Avoid markdown symbols. Use titles like 'Project Overview:' instead of markdown headers."
    )

    documentation_text = call_openai(prompt)
    sections = parse_sections(documentation_text)
    write_to_pdf_with_toc(sections, output_pdf_path)

