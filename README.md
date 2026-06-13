# ✨ TextDigest AI Summarizer

> An intelligent document summarizer powered by Google Gemini AI — upload a file or paste text and get a clean, concise summary in seconds.
> 
---

Live preview : https://textdigest-ai-summarizer.streamlit.app/

## 📌 Overview

**TextDigest AI Summarizer** is a web application built with Streamlit that lets you summarize any text or document instantly. Powered by Google's Gemini 2.5 Flash model, it supports three summary lengths and exports results as a downloadable PDF.

---

## 🚀 Features

- 📄 **File Upload** — supports PDF, DOCX, and TXT formats
- ✏️ **Manual Text Input** — paste any text directly
- 🎚️ **Three Summary Lengths** — Short (1–2 sentences), Medium, or Detailed
- 📋 **Copy to Clipboard** — one-click copy of the generated summary
- ⬇️ **Download as PDF** — export your summary with a single click
- 🎨 **Lavender UI** — clean, modern interface with a purple theme

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | Streamlit |
| AI Model | Google Gemini 2.5 Flash |
| PDF Reading | PyPDF2 |
| DOCX Reading | python-docx |
| PDF Export | ReportLab |
| Language | Python 3.9+ |

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Lvgs3033/TextDigest-AI-Summarizer.git
cd TextDigest-AI-Summarizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Create a `.streamlit/secrets.toml` file in the project root:

```toml
GOOGLE_API_KEY = "your-gemini-api-key-here"
```

> Get your free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📦 Requirements

Create a `requirements.txt` with the following:

```
streamlit
google-generativeai
PyPDF2
python-docx
reportlab
```

---

## 📁 Project Structure

```
TextDigest-AI-Summarizer/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API keys (local only, not committed)
└── README.md               # Project documentation
```

---

## 🖥️ Usage

1. Open the app in your browser
2. Choose **Upload a File** or **Enter Text Manually**
3. Select your preferred **Summary Length**
4. Click **✨ Generate Summary**
5. Copy or download your summary

---
