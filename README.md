In order to run the script, you can go one of two ways:

# **OpenAI:**
Generate an API key using your OpenAI account and replace the placeholder "YOUR_API_KEY" in GenDocOpenAI.py with that key. Run the script RunGenDoc.py by using the command "streamlit run RunGenDoc.py".

*NOTE:* must install the dependencies using the command "pip install streamlit python-docx PyPDF2 reportlab openai" or create a requirements.txt file.

# **LLaMa:**
Run the script GenDocLlama.py by using the command "streamlit run GenDocLlama.py".
You must download llama-2-7b.Q4_K_M.gguf from TheBloke on HuggingFace. The link is https://huggingface.co/TheBloke/Llama-2-7B-GGUF

*NOTE:* must install the dependencies using the command "pip install streamlit python-docx PyPDF2 reportlab llama-cpp-python" or create a requirements.txt file. This version of the script will run much slower due to the model running locally (if you need a free LLM to use).
