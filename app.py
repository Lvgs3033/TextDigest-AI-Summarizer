import streamlit as st
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
import math

# Configure Gemini API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Text extraction
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n\n".join([p.extract_text().rstrip() for p in reader.pages if p.extract_text()]).strip()

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n\n".join([p.text.rstrip() for p in doc.paragraphs if p.text]).strip()

def extract_text_from_txt(file):
    raw = file.read()
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="ignore")
    return str(raw)

# Summary Instructions
summary_instructions = {
    "Short (1-2 sentences)": "Write a very concise summary in 1-2 sentences, capturing only the main idea.",
    "Medium": "Write a clear and coherent summary in a short paragraph, highlighting the key points.",
    "Detailed": "Write a detailed summary in multiple paragraphs, covering all important information with clear structure."
}

# Summarization
def summarize_text(text, length):
    prompt = f"""
    You are an expert text summarizer. {summary_instructions[length]}

    Original Text:
    {text}

    Provide the summary in clear, grammatically correct language. Maintain key details, context, and logical flow. Do not include unrelated information or filler.
    """
    response = model.generate_content(prompt)
    return getattr(response, "text", str(response))

# PDF Creation
def create_pdf_bytes(summary_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin = 40
    right_margin = 40
    usable_width = width - left_margin - right_margin
    y = height - 60
    pdf.setFont("Times-Roman", 12)
    words = summary_text.split()
    line = ""
    for word in words:
        test_line = line + " " + word if line else word
        if pdf.stringWidth(test_line, "Times-Roman", 12) <= usable_width:
            line = test_line
        else:
            pdf.drawString(left_margin, y, line)
            y -= 18
            line = word
            if y < 60:
                pdf.showPage()
                pdf.setFont("Times-Roman", 12)
                y = height - 60
    if line:
        pdf.drawString(left_margin, y, line)
    pdf.save()
    buffer.seek(0)
    return buffer.read()

# Streamlit App
st.set_page_config(page_title="TextDigest AI Summarizer", layout="wide", page_icon="✨")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');

/* ── Base ── */
.stApp {
    background: linear-gradient(145deg, #f3f0ff 0%, #ede9fe 40%, #faf5ff 100%);
    font-family: 'Inter', sans-serif;
}

/* ── Header ── */
.header {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%);
    color: white;
    border-radius: 20px;
    padding: 36px 28px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.35);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.header::after {
    content: '';
    position: absolute;
    bottom: -50px; left: -30px;
    width: 140px; height: 140px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
.header p {
    margin: 0;
    opacity: 0.92;
    font-size: 15px;
    font-weight: 400;
    letter-spacing: 0.2px;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 4px 24px rgba(124, 58, 237, 0.08);
    border: 1px solid rgba(196, 181, 253, 0.4);
    margin-bottom: 18px;
}

/* ── Streamlit button overrides ── */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45) !important;
    background: linear-gradient(135deg, #6d28d9, #9333ea) !important;
}
div.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Active / selected mode button */
div[data-testid="column"] div.stButton > button[kind="secondary"] {
    background: rgba(237, 233, 254, 0.6) !important;
    color: #6d28d9 !important;
    border: 1.5px solid #c4b5fd !important;
    box-shadow: none !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1.5px solid #c4b5fd !important;
    background: rgba(255,255,255,0.8) !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
}

/* ── Text area ── */
div[data-testid="stTextArea"] textarea {
    border-radius: 12px !important;
    border: 1.5px solid #c4b5fd !important;
    background: rgba(255,255,255,0.85) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: #3b0764 !important;
    transition: border-color 0.2s;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.12) !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] > section {
    border: 2px dashed #c4b5fd !important;
    border-radius: 14px !important;
    background: rgba(245, 243, 255, 0.6) !important;
    transition: border-color 0.2s;
}
div[data-testid="stFileUploader"] > section:hover {
    border-color: #7c3aed !important;
    background: rgba(237, 233, 254, 0.5) !important;
}

/* ── Labels ── */
label[data-testid="stWidgetLabel"] p,
div[data-testid="stFileUploader"] label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #5b21b6 !important;
    font-size: 14px !important;
    letter-spacing: 0.2px;
}

/* ── Alert / error ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-color: #a855f7 !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(196, 181, 253, 0.35) !important;
    margin: 20px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f3f0ff; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #a78bfa; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <h1>✨ TextDigest AI Summarizer</h1>
    <p>Upload a document or paste your text — get a clean, intelligent summary in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
if "input_mode" not in st.session_state:
    st.session_state.input_mode = None
if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""
if "text_content" not in st.session_state:
    st.session_state.text_content = ""

# ── Mode selector ────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("📄  Upload a File", key="btn_upload"):
        if st.session_state.input_mode != "upload":
            st.session_state.summary_text = ""
            st.session_state.text_content = ""
        st.session_state.input_mode = "upload"
with col2:
    if st.button("✏️  Enter Text Manually", key="btn_text"):
        if st.session_state.input_mode != "manual":
            st.session_state.summary_text = ""
            st.session_state.text_content = ""
        st.session_state.input_mode = "manual"

st.markdown("<br>", unsafe_allow_html=True)

# ── Input Area ───────────────────────────────────────────────────────────────
if st.session_state.input_mode == "upload":
    uploaded_file = st.file_uploader("Choose a file (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()
        try:
            if ext == "pdf":
                st.session_state.text_content = extract_text_from_pdf(uploaded_file)
            elif ext == "docx":
                st.session_state.text_content = extract_text_from_docx(uploaded_file)
            elif ext == "txt":
                st.session_state.text_content = extract_text_from_txt(uploaded_file)
            st.success(f"✅ **{uploaded_file.name}** loaded successfully — {len(st.session_state.text_content):,} characters")
        except Exception:
            st.error("⚠️ Could not read the file. Please try a different one.")

elif st.session_state.input_mode == "manual":
    st.session_state.text_content = st.text_area(
        "Paste your text here:",
        height=260,
        placeholder="Start typing or paste any text you'd like summarised…"
    )

# ── Summarize ────────────────────────────────────────────────────────────────
if st.session_state.text_content:
    text_content = st.session_state.text_content

    st.markdown("<hr>", unsafe_allow_html=True)

    length = st.selectbox(
        "Summary length",
        ["Short (1-2 sentences)", "Medium", "Detailed"],
        index=1
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✨  Generate Summary", key="btn_generate"):
        with st.spinner("Summarising…"):
            summary_text = summarize_text(text_content, length)

        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area("Your Summary", value=summary_text, height=260, key="summary_out")

        summary_b64 = base64.b64encode(summary_text.encode("utf-8")).decode("utf-8")
        pdf_b64 = base64.b64encode(create_pdf_bytes(summary_text)).decode()

        action_html = f"""
        <div style="display:flex; justify-content:center; gap:14px; margin-top:14px; flex-wrap:wrap;">

            <button onclick="
                const text = atob('{summary_b64}');
                navigator.clipboard.writeText(text)
                    .then(() => {{
                        this.innerText = '✅ Copied!';
                        setTimeout(() => {{ this.innerText = '📋 Copy Summary'; }}, 2000);
                    }})
                    .catch(err => alert('Copy failed: ' + err));
            "
            style="
                padding: 11px 22px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                border-radius: 10px;
                background: linear-gradient(135deg, #7c3aed, #a855f7);
                color: white;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 14px rgba(124,58,237,0.3);
                transition: opacity 0.2s;
            "
            onmouseover="this.style.opacity='0.85'"
            onmouseout="this.style.opacity='1'">
                📋 Copy Summary
            </button>

            <a download="summary.pdf" href="data:application/pdf;base64,{pdf_b64}"
               style="text-decoration:none;">
                <button type="button"
                style="
                    padding: 11px 22px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Inter', sans-serif;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #6d28d9, #8b5cf6);
                    color: white;
                    border: none;
                    cursor: pointer;
                    box-shadow: 0 4px 14px rgba(109,40,217,0.3);
                    transition: opacity 0.2s;
                "
                onmouseover="this.style.opacity='0.85'"
                onmouseout="this.style.opacity='1'">
                    ⬇️ Download PDF
                </button>
            </a>

        </div>
        """
        st.components.v1.html(action_html, height=75)