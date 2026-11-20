import os, re, random
from collections import Counter
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None

st.set_page_config(page_title="AI StudyMate", page_icon="📚", layout="wide")

# ------------------- Helpers -------------------
def split_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if len(s.strip()) > 15]

STOPWORDS = set("a an the and or but if while is are was were be been being to of in on at for from by with as into than then that this these those it its their they them he she we you your i my our can could should would may might will do does did have has had not no so very also about over under after before more most some any each other such what when where why how".split())

def tokenize(text):
    return [w for w in re.findall(r"[a-zA-Z']+", text.lower()) if w not in STOPWORDS and len(w) > 2]

def local_summary(text, count=4):
    sentences = split_sentences(text)
    if not sentences:
        return "Please provide a little more text (at least a few complete sentences) to summarize."
    words = tokenize(text)
    freq = Counter(words)
    scored = []
    for i, s in enumerate(sentences):
        terms = tokenize(s)
        score = sum(freq[t] for t in terms) / max(len(terms), 1)
        scored.append((score, i, s))
    chosen = sorted(sorted(scored, reverse=True)[:min(count, len(sentences))], key=lambda x: x[1])
    return "\n\n".join("• " + s for _, _, s in chosen)

def local_answer(text, question):
    sentences = split_sentences(text)
    qterms = set(tokenize(question))
    ranked = (sorted(sentences, key=lambda s: len(qterms & set(tokenize(s))), reverse=True)
              if qterms else sentences)
    if not ranked or (qterms and not (qterms & set(tokenize(ranked[0])))):
        return "I couldn't find a clear answer in the supplied notes. Try rephrasing your question or adding relevant material."
    return "Based on your notes:\n\n" + "\n\n".join(ranked[:2])

def local_quiz(text, n=5):
    sentences = split_sentences(text)
    candidates = [s for s in sentences if len(tokenize(s)) >= 5]
    if not candidates:
        return []
    random.seed(17)
    random.shuffle(candidates)
    result = []
    for sentence in candidates[:n]:
        words = tokenize(sentence)
        answer = max(words, key=lambda w: len(w)) if words else "key concept"
        blanked = re.sub(rf"\b{re.escape(answer)}\b", "____", sentence, count=1, flags=re.I)
        result.append((blanked, answer))
    return result

POSITIVE = set("good great excellent helpful useful clear easy love loved happy positive amazing best interesting success successful enjoy enjoyed improve improvement confident exciting effective reliable wonderful".split())
NEGATIVE = set("bad poor difficult confusing hard hate hated sad negative worse worst fail failure problem broken useless annoying frustrating disappointing".split())
def sentiment(text):
    words = tokenize(text)
    p, n = sum(w in POSITIVE for w in words), sum(w in NEGATIVE for w in words)
    if p > n: return "Positive", p, n
    if n > p: return "Negative", p, n
    return "Neutral", p, n

# Optional cloud mode: Azure OpenAI configured through environment variables.
def azure_chat(prompt, system="You are a careful study assistant. Use only the supplied notes when answering. If information is absent, say so."):
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    if not (endpoint and key and deployment and AzureOpenAI):
        return None
    client = AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version=api_version)
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content

# ------------------- UI -------------------
st.markdown("""<style>
.block-container {padding-top: 1.7rem; max-width: 1150px;}
.hero {padding: 1.3rem 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#142d4e,#247e9b); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin-bottom:.2rem;} .hero p {color:#d9eef8; margin:0;}
div[data-testid='stMetric'] {background:#f3f7fb;padding:12px;border-radius:12px;}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>📚 AI StudyMate</h1><p>Your intelligent study companion — summarize, ask, quiz, and analyze text.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("StudyMate Menu")
    st.caption("AI learning tools")
    mode = st.radio("Processing mode", ["Local demo (offline)", "Azure AI (optional)"], help="Local mode works without credentials. Azure mode uses your configured Azure OpenAI deployment.")
    st.divider()
    st.markdown("**Project concepts**")
    st.write("• NLP and text processing\n• Prompt-based AI\n• Question answering\n• Sentiment analysis\n• Responsible AI")
    st.caption("Prototype: verify generated outputs before relying on them.")

uploaded = st.file_uploader("Upload study notes (.txt) or paste text below", type=["txt"])
file_text = uploaded.getvalue().decode("utf-8", errors="ignore") if uploaded else ""
notes = st.text_area("Study material", value=file_text, height=220, placeholder="Paste your notes here...", help="Text is processed locally unless Azure mode is selected and configured.")
words = len(tokenize(notes)) if notes else 0
col1, col2, col3 = st.columns(3)
col1.metric("Words", words)
col2.metric("Sentences", len(split_sentences(notes)) if notes else 0)
col3.metric("Mode", "Azure" if mode.startswith("Azure") else "Local")

if not notes.strip():
    st.info("Add notes above to activate StudyMate's tools. Try the sample material in the project folder.")
else:
    tabs = st.tabs(["✨ Summary", "💬 Ask questions", "📝 Quiz", "📊 Sentiment"])
    with tabs[0]:
        st.subheader("Smart Summary")
        if st.button("Generate summary", type="primary", key="summary"):
            with st.spinner("Summarizing..."):
                out = azure_chat("Summarize these notes into concise bullet points with key concepts and definitions.\n\nNOTES:\n" + notes) if mode.startswith("Azure") else None
                st.markdown(out if out else local_summary(notes))
                if mode.startswith("Azure") and not out: st.warning("Azure settings are missing. Showing the local demo summary instead.")
    with tabs[1]:
        st.subheader("Ask about your material")
        question = st.text_input("Your question", placeholder="e.g. What is NLP?")
        if st.button("Find answer", key="ask") and question.strip():
            out = azure_chat("Answer the question using only these notes. If the answer is not in the notes, say so.\nQUESTION: " + question + "\nNOTES:\n" + notes) if mode.startswith("Azure") else None
            st.markdown(out if out else local_answer(notes, question))
            if mode.startswith("Azure") and not out: st.warning("Azure settings are missing. Showing the local demo answer instead.")
    with tabs[2]:
        st.subheader("Practice quiz")
        if st.button("Generate quiz", key="quiz"):
            out = azure_chat("Create 5 short quiz questions with answers based only on these notes. Format as numbered questions then an Answer Key.\n\nNOTES:\n" + notes) if mode.startswith("Azure") else None
            if out:
                st.markdown(out)
            else:
                quiz = local_quiz(notes)
                if quiz:
                    for i, (q, a) in enumerate(quiz, 1):
                        st.markdown(f"**Q{i}.** {q}")
                        with st.expander("Reveal answer"):
                            st.write(a)
                else: st.warning("Add more complete sentences to generate a quiz.")
            if mode.startswith("Azure") and not out: st.warning("Azure settings are missing. Showing the local demo quiz instead.")
    with tabs[3]:
        st.subheader("Sentiment analyzer")
        sample = st.text_area("Enter a sentence to analyze", placeholder="The lesson was clear and helpful.", key="sentiment_text")
        if st.button("Analyze sentiment", key="sentiment"):
            label, positive, negative = sentiment(sample)
            st.metric("Result", label)
            st.write(f"Positive keyword matches: **{positive}** · Negative keyword matches: **{negative}**")
            st.caption("This is a simple lexicon-based demonstration, not a trained or cloud sentiment model.")

st.divider()
st.caption("AI StudyMate | Course project prototype | Outputs may be incomplete or inaccurate. Use your notes as the source of truth.")
