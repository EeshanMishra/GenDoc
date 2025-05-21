import streamlit as st
import os
import tempfile
from datetime import datetime
from GenDoc import generate_documentation  # Replace with the filename of your previous script

st.set_page_config(page_title="AI Documentation Generator", layout="centered")
st.title("📄 AI Project Documentation Generator")

st.markdown("Upload your project files and get a well-formatted PDF document with automatic documentation.")

# User Inputs
project_description = st.text_area("📝 Project Description", placeholder="e.g., A Flask API to manage IoT devices and store data in PostgreSQL", height=100)

req_files = st.file_uploader("📚 Upload Requirement Files (.pdf or .docx)", type=["pdf", "docx"], accept_multiple_files=True)
code_files = st.file_uploader("🧑‍💻 Upload Code Files", type=None, accept_multiple_files=True)
email_files = st.file_uploader("✉️ Upload Email Threads (.eml)", type=["eml"], accept_multiple_files=True)

if st.button("🚀 Generate Documentation"):
    if not project_description:
        st.warning("Please enter a project description.")
    elif not req_files and not code_files:
        st.warning("Please upload at least one requirements or code file.")
    else:
        with st.spinner("Generating your documentation..."):

            with tempfile.TemporaryDirectory() as tmpdir:
                # Save uploaded files
                def save_uploaded_files(files):
                    paths = []
                    for f in files:
                        file_path = os.path.join(tmpdir, f.name)
                        with open(file_path, "wb") as out:
                            out.write(f.read())
                        paths.append(file_path)
                    return paths

                req_paths = save_uploaded_files(req_files)
                code_paths = save_uploaded_files(code_files)
                email_paths = save_uploaded_files(email_files)

                output_pdf_path = os.path.join(tmpdir, f"documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

                generate_documentation(
                    project_description=project_description,
                    req_files=req_paths,
                    code_files=code_paths,
                    email_files=email_paths,
                    output_pdf_path=output_pdf_path
                )

                with open(output_pdf_path, "rb") as f:
                    st.success("✅ Documentation generated successfully!")
                    st.download_button("📥 Download PDF", f, file_name="project_documentation.pdf", mime="application/pdf")
