# AI StudyMate — Intelligent Study Assistant

A small student project demonstrating AI/NLP concepts with an interactive Streamlit UI.


## Features
- Smart summarizer (local extractive summary; optional Azure OpenAI summary)
- Notes-based question answering (local sentence matching; optional Azure OpenAI)
- Quiz generator (local fill-in-the-blank; optional Azure OpenAI quiz)
- Lexicon-based sentiment analysis (positive/negative/neutral)
- Upload `.txt` notes or paste content

## Run locally (Windows)
1. Install Python 3.10+ from python.org and ensure Python is added to PATH.
2. Extract the ZIP folder.
3. Open Command Prompt in the project folder.
4. Run:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```
5. Browser opens the app. Upload `sample_notes.txt` or paste notes.

## Local mode
Local demo works without Azure credentials or internet after packages are installed. Its summary, Q&A and quiz are heuristic demonstrations; sentiment uses a small word list. Do not describe these as a production AI model.


## Optional Azure OpenAI mode
If you have access to an Azure OpenAI deployment, copy `.env.example` to `.env` and fill the values. The app loads `.env` automatically. It reads:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

For Windows Command Prompt, set variables in the same terminal (example):
```
set AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
set AZURE_OPENAI_API_KEY=YOUR_KEY
set AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT
set AZURE_OPENAI_API_VERSION=2024-10-21
streamlit run app.py
```
Keep keys private. Never upload a populated `.env` or share API keys in screenshots/reports.


## Project scope / limitations
- This is an educational prototype, not a production system.
- Local Q&A uses keyword matching; local quiz uses fill-in-the-blank heuristics.
- Local sentiment uses a small keyword lexicon and cannot reliably understand sarcasm, context, or nuanced language.
- Azure OpenAI mode is optional and requires an endpoint, key, and model deployment; no credentials are included.
- Always validate AI output and avoid entering confidential or personal information.

## Viva focus
Be able to explain: NLP, generative AI, prompt engineering, text summarization, question answering, sentiment analysis, Azure AI, API/key security, responsible AI, and the difference between the local demo and a deployed AI service.
