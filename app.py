import html
import time

import markdown
import streamlit as st
from dotenv import load_dotenv

# Load .env BEFORE importing project modules (they read env vars at import time)
load_dotenv()

from utils.ffmpeg_setup import ensure_ffmpeg
import os
import time
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question

# ─── Page Config (must be the first Streamlit call) ─────────────────────────────

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── FFmpeg check (friendly error instead of a crash) ───────────────────────────
try:
    ensure_ffmpeg()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# ─── Custom CSS ─────────────────────────────────────────────────────────────────

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Grid Background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.card:hover { border-color: var(--accent); }
.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 3px;
    height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

.card-content { font-size: 0.875rem; line-height: 1.7; color: var(--text); }
.card-content ul { padding-left: 1.2rem; margin: 0.4rem 0; }
.card-content p { margin: 0.4rem 0; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }


.badge-purple {
    background: rgba(124,58,237,0.2);
    color: var(--accent-glow);
    border: 1px solid rgba(124,58,237,0.3);
}

.badge-cyan {
    background: rgba(6,182,212,0.15);
    color: var(--accent-2);
    border: 1px solid rgba(6,182,212,0.3);
}

.badge-green {
    background: rgba(16,185,129,0.15);
    color: var(--success);
    border: 1px solid rgba(16,185,129,0.3);
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

.stButton > button, .stFormSubmitButton > button {
/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    text-transform: uppercase !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
}

[data-testid="stForm"] { border: none !important; padding: 0 !important; }


/* ── Status ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-active  { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done    { background: var(--success); }
.dot-pending { background: var(--border); }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-msg { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.2rem; }
.chat-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; }
.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
}
.user-label { color: var(--accent-glow); }
.bot-label  { color: var(--accent-2); }
.user-bubble { background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.25); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.1);  border: 1px solid rgba(6,182,212,0.2);   align-self: flex-start; }
.chat-bubble p { margin: 0.2rem 0; }
.chat-bubble ul { padding-left: 1.2rem; margin: 0.3rem 0; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active {
    background: var(--accent-glow);
    box-shadow: 0 0 8px var(--accent-glow);
    animation: pulse 1.5s infinite;
}

.dot-done {
    background: var(--success);
}

.dot-pending {
    background: var(--border);
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Transcript ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────────
for key, default in {
/* ── General ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

.stProgress > div > div > div {
    background: var(--accent) !important;
}

[data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
}

label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 5px;
    height: 5px;
}

::-webkit-scrollbar-track {
    background: var(--bg);
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def save_uploaded_file(uploaded_file):
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    original_name = Path(uploaded_file.name)
    unique_name = f"{uuid.uuid4().hex}_{original_name.name}"
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(file_path)


STEPS = [
    ("audio",      "🔊", "Audio Processing"),
    ("transcript", "📝", "Transcription"),
    ("title",      "🏷️", "Title Generation"),
    ("summary",    "📋", "Summarisation"),
    ("extract",    "🔍", "Extraction"),
    ("rag",        "🧠", "RAG Engine"),
]


# ─── Helpers ────────────────────────────────────────────────────────────────────
def to_html(text: str) -> str:
    """Escape raw HTML from LLM output, then render markdown (bullets, bold...)."""
    return markdown.markdown(html.escape(text or "", quote=False), extensions=["nl2br"])


def step_class(key: str) -> str:
    s = st.session_state.pipeline_steps.get(key, "pending")
    return {"active": "dot-active", "done": "dot-done"}.get(s, "dot-pending")

def step_status(steps: dict, key: str) -> str:
    status = steps.get(key, "pending")
    if status == "active":
        return "dot-active"
    if status == "done":
        return "dot-done"
    return "dot-pending"


def render_step_bar(label: str, key: str, icon: str):
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {step_class(key)}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)


def card(title: str, body_html: str):
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-content">{body_html}</div>
    </div>""", unsafe_allow_html=True)


# ─── Sidebar ────────────────────────────────────────────────────────────────────
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(
        f"""
        <div class="status-bar">
            <div class="status-dot {css}"></div>
            <span>{icon} {label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '''
        <div class="hero-title" style="font-size:1.6rem">
            🎬 AI<br>Video
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-sub">Meeting Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown('<span class="badge badge-purple">Input</span>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or D:\\videos\\meeting.mp4",
    )

    language = st.selectbox("Language", ["english", "hindi", "hinglish"], index=0)

    run_btn = st.button("⚡  Analyse", use_container_width=True)

    input_method = st.radio(
        "Choose Input",
        [
            "YouTube URL",
            "Upload Video / Audio",
            "Local File Path",
        ],
    )

    source = None

    if input_method == "YouTube URL":
        source = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
        )
        st.caption("⚠️ YouTube may block requests from cloud servers (HTTP 403). Uploading a file is recommended for Streamlit Cloud.")

    elif input_method == "Upload Video / Audio":
        uploaded_file = st.file_uploader(
            "Upload Video or Audio",
            type=["mp4", "mp3", "wav", "m4a", "webm", "ogg", "aac", "flac"],
        )
        if uploaded_file is not None:
            st.success(f"Selected: {uploaded_file.name}")
            st.caption(f"File size: {uploaded_file.size / (1024 * 1024):.2f} MB")
            source = uploaded_file

    else:
        source = st.text_input(
            "Local File Path",
            placeholder="C:/Videos/meeting.mp4",
        )

    language = st.selectbox(
        "Language",
        ["english", "hindi", "hinglish"],
        index=0,
    )

    run_btn = st.button("⚡ Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for key, icon, label in STEPS:
            render_step_bar(label, key, icon)
        pipeline_items = [
            ("audio", "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title", "🏷️", "Title Generation"),
            ("summary", "📋", "Summarisation"),
            ("extract", "🔍", "Extraction"),
            ("rag", "🧠", "RAG Engine"),
        ]
        for step, icon, label in pipeline_items:
            render_step_bar(label, step, icon)


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>', unsafe_allow_html=True)
st.markdown("---")


# ============================================================
# RUN PIPELINE
# ============================================================

if run_btn:
    clean_source = source.strip().strip('"')

    if not clean_source:
        st.error("Please enter a YouTube URL or file path.")
    if source is None or (isinstance(source, str) and not source.strip()):
        st.error("Please provide a YouTube URL or upload a video/audio file.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        failed = False

        with st.status("Running pipeline…", expanded=True) as status:

            def run_step(key, label, fn, *args):
                st.session_state.pipeline_steps[key] = "active"
                st.write(f"⏳ {label}…")
                out = fn(*args)
                st.session_state.pipeline_steps[key] = "done"
                st.write(f"✅ {label}")
                return out

            try:
                chunks = run_step("audio", "Processing audio", process_input, clean_source)
                transcript = run_step("transcript", "Transcribing", transcribe_all, chunks, language)
                title = run_step("title", "Generating title", generate_title, transcript)
                summary = run_step("summary", "Summarising", summarize, transcript)
        try:
            if hasattr(source, "getbuffer"):
                with progress_placeholder.container():
                    st.info("📁 Saving uploaded file...")
                source_path = save_uploaded_file(source)
            else:
                source_path = source.strip()

            with progress_placeholder.container():
                st.info("⚙️ Pipeline running...")

            update_step("audio", "active")
            chunks = process_input(source_path)
            update_step("audio", "done")

                def _extract_all(t):
                    return (
                        extract_action_items(t),
                        extract_key_decisions(t),
                        extract_questions(t),
                    )

                action_items, decisions, questions = run_step(
                    "extract", "Extracting action items, decisions, questions", _extract_all, transcript
                )
                rag_chain = run_step("rag", "Building chat index", build_rag_chain, transcript)

                st.session_state.result = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "rag_chain": rag_chain,
                }
                st.session_state.pipeline_done = True
                status.update(label="Analysis complete", state="complete", expanded=False)

            except Exception as e:
                failed = True
                for k, s in list(st.session_state.pipeline_steps.items()):
                    if s == "active":
                        st.session_state.pipeline_steps[k] = "pending"
                status.update(label="Pipeline failed", state="error", expanded=True)
                st.error(f"❌ {e}")

        if not failed:
            time.sleep(0.3)
            st.rerun()

# ── Results ─────────────────────────────────────────────────────────────────────
            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions = extract_key_decisions(transcript)
            questions = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }

            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.8)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for step in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(step) == "active":
                    st.session_state.pipeline_steps[step] = "pending"

            error_text = str(e)
            if "403" in error_text or "Forbidden" in error_text:
                progress_placeholder.error(
                    "❌ YouTube blocked this request (HTTP 403 Forbidden).\n\n"
                    "Please use **Upload Video / Audio** for the most reliable experience."
                )
            else:
                progress_placeholder.error(f"❌ Error: {error_text}")


# ============================================================
# RESULTS
# ============================================================

if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {html.escape(r['title'])}
        <div style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700; color:var(--text);">
            {r["title"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        card("📋 Summary", to_html(r["summary"]))

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(
                f'<div class="transcript-box">{html.escape(r["transcript"])}</div>',
                unsafe_allow_html=True,
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r["summary"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.text_area(
                "Transcript",
                value=r["transcript"],
                height=300,
                label_visibility="collapsed",
            )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        card("✅ Action Items", to_html(r["action_items"]))
    with c2:
        card("🔑 Key Decisions", to_html(r["key_decisions"]))
    with c3:
        card("❓ Open Questions", to_html(r["open_questions"]))

    st.markdown("---")

    # ── RAG Chat ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">'
        '💬 Chat with your Meeting</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{html.escape(msg['content'])}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{to_html(msg['content'])}</div>
                </div>"""
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        chat_col1, chat_col2 = st.columns([5, 1], gap="small")
        with chat_col1:
            user_input = st.text_input(
                "Your question",
                placeholder="What were the main decisions made?",
                label_visibility="collapsed",
            )
        with chat_col2:
            send_btn = st.form_submit_button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        question = user_input.strip()
        try:
            with st.spinner("Thinking…"):
                answer = ask_question(r["rag_chain"], question)
        except Exception as e:
            answer = f"Sorry, something went wrong: {e}"
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r["action_items"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r["key_decisions"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r["open_questions"]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; margin-bottom:1rem;">
        💬 Chat with your Meeting
    </div>
    """, unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    user_input = st.chat_input("Ask anything about your meeting...")

    if user_input and user_input.strip():
        question = user_input.strip()

        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(r["rag_chain"], question)
            st.write(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
        })

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:5rem 2rem; text-align:center;">
        <div style="font-size:4rem; margin-bottom:1rem;">🎬</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:700; color:var(--text); margin-bottom:0.5rem;">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted); font-size:0.85rem; max-width:450px; line-height:1.7;">
            Paste a YouTube URL or upload a video/audio file in the sidebar. Uploading a file is the most reliable option on Streamlit Cloud.
        </div>
        <div style="margin-top:2rem; display:flex; gap:1rem; flex-wrap:wrap; justify-content:center;">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
