# 🧠 Autonomous Research / Content Agent

An agentic AI system that performs **multi-step research, analysis, and report generation** using web data, local knowledge, and uploaded documents.

---

## 🌐 Live Demo

👉 https://autonomous-research-agent-7wtkgllwpvtgs8cdyz4tcs.streamlit.app

---

## 🧠 What this project does

* Receives a research prompt
* Searches the web (OpenAI Responses API)
* Retrieves relevant local documents
* Processes uploaded PDFs
* Generates a structured research report with insights and references

---

## 🎯 Why this matters

Modern AI is moving beyond single prompts into **agentic workflows**.

This project demonstrates how to:
- break problems into steps  
- use tools (web search, documents)  
- generate structured, explainable outputs  

👉 This is **exactly the direction of real-world AI systems today**

---

## 🚀 Features

* 🤖 Multi-agent pipeline (Research → Analysis → Writer)
* 🌐 Web search integration (OpenAI)
* 📄 PDF upload + processing
* 📚 Local knowledge base search
* 🧠 Structured JSON report output
* 🔁 Fallback mode (works without OpenAI)
* 💾 Downloadable results
* 🌐 Interactive Streamlit app

---

## 🛠 Tech Stack

* Python
* OpenAI API (Responses API)
* Streamlit
* Pydantic
* scikit-learn (local retrieval)
* pypdf

---

## ⚙️ How it works

1. **Research Agent**  
   Gathers information from:
   - web search  
   - local documents  
   - uploaded PDFs  

2. **Analysis Agent**  
   Extracts:
   - key insights  
   - patterns  
   - implications  

3. **Writer Agent**  
   Produces:
   - executive summary  
   - recommendations  
   - structured report  

---

## ▶️ Run locally

```bash
git clone https://github.com/dealmeidaferreiraAlexandra/autonomous-research-agent.git
cd autonomous-research-agent

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env


## ▶️ Add your API key in .env:

OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-5.5

## ▶️ Run the app:

streamlit run app.py

🔐 API Key (IMPORTANT)

This project uses:

.env for local development
Streamlit Secrets for deployment

👉 Never commit your API key

⚠️ Notes
Web search requires OpenAI API access
If no API key is available → app runs in local fallback mode
PDF extraction depends on text-based PDFs

👩‍💻 Author

Developed by Alexandra de Almeida Ferreira
GitHub: https://github.com/dealmeidaferreiraAlexandra
LinkedIn: https://www.linkedin.com/in/dealmeidaferreira

📄 License

This project is licensed under the MIT License.