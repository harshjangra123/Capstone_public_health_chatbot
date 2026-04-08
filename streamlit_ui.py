import streamlit as st
import requests
import markdown

st.set_page_config(page_title="HealthBot", layout="centered", page_icon="🩺")

# ─── HIDE STREAMLIT CHROME ───────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stDeployButton"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─── GLOBAL STYLES ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@700;800&display=swap');

/* ── ROOT VARS ── */
:root {
    --bg:       #FFF8F0;
    --black:    #1C1C1C;
    --border:   #1C1C1C;
    --shadow:   3px 3px 0px #1C1C1C;
    --shadow-lg:5px 5px 0px #1C1C1C;

    /* pastel palette */
    --red:      #FF8FAB;
    --yellow:   #FFE066;
    --green:    #B5EAD7;
    --blue:     #AEC6F6;
    --lavender: #D4BBFF;
    --peach:    #FFCBA4;

    --user-bg:  #FFD6E0;
    --bot-bg:   #E8F4FF;
    --header-bg:#1C1C1C;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stApp"], [data-testid="stMain"], .stApp, .main {
    background-color: var(--bg) !important;
    font-family: 'Space Mono', monospace !important;
}

/* Kill any black bars on sides — ensure full viewport is covered */
body::before, body::after { display: none !important; }
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
[data-testid="stHeader"],
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
.stApp > div,
[data-testid="stBottom"],
.stMainBlockContainer,
.appview-container,
.main > .block-container,
section.main {
    background-color: var(--bg) !important;
}
            
.st-emotion-cache-hzygls {
    background-color: transparent !important;            
}

/* Nuke any black body/root background that bleeds around centered container */
body {
    background-color: var(--bg) !important;
}
#root, #root > div {
    background-color: var(--bg) !important;
}

.block-container {
    padding: 0 !important;
    margin: 0 auto !important;
    max-width: 760px !important;
}

/* Bottom padding so last message isn't hidden behind input bar */
section.main {
    padding-bottom: 120px !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--black); }

/* ── HEADER ── */
.nb-header {
    background: var(--header-bg);
    border-bottom: 3px solid var(--red);
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 999;
    animation: slideDown 0.45s cubic-bezier(0.16,1,0.3,1) both;
}
@keyframes slideDown {
    from { transform: translateY(-80px); opacity: 0; }
    to   { transform: translateY(0);     opacity: 1; }
}
.nb-logo {
    width: 40px; height: 40px;
    background: var(--red);
    border: 2.5px solid #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.nb-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 800;
    color: #FFF8F0;
    letter-spacing: -0.3px;
    text-transform: uppercase;
    line-height: 1;
}
.nb-subtitle {
    font-size: 9px; color: var(--red);
    letter-spacing: 2.5px; text-transform: uppercase;
    margin-top: 3px;
}
.nb-status {
    margin-left: auto;
    display: flex; align-items: center; gap: 6px;
    font-size: 10px; color: #888; letter-spacing: 1px; text-transform: uppercase;
}
.nb-dot {
    width: 7px; height: 7px;
    background: var(--green); border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity:1; } 50% { opacity:0.25; }
}

/* ── CHAT WRAPPER ── */
.nb-chat {
    padding: 24px 20px 8px;
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* ── WELCOME CARD ── */
.nb-welcome {
    background: var(--yellow);
    border: 2.5px solid var(--border);
    box-shadow: var(--shadow-lg);
    padding: 18px 22px;
    margin-bottom: 24px;
    animation: popIn 0.55s cubic-bezier(0.16,1,0.3,1) 0.15s both;
}
@keyframes popIn {
    from { transform: translateY(12px) scale(0.97); opacity: 0; }
    to   { transform: translateY(0)    scale(1);    opacity: 1; }
}
.nb-welcome-title {
    font-family: 'Syne', sans-serif;
    font-size: 16px; font-weight: 800;
    color: var(--black); text-transform: uppercase; margin-bottom: 6px;
}
.nb-welcome-text {
    font-size: 11px; color: var(--black); line-height: 1.65; opacity: 0.72;
}
.nb-tags {
    display: flex; flex-wrap: wrap; gap: 7px; margin-top: 14px;
}
.nb-tag {
    background: var(--black); color: var(--yellow);
    font-size: 9px; padding: 4px 10px;
    letter-spacing: 1.5px; text-transform: uppercase;
    border: 2px solid var(--black);
    transition: all 0.12s; cursor: default;
}
.nb-tag:hover {
    background: var(--red); border-color: var(--black); color: var(--black);
    transform: translate(-1px,-1px);
    box-shadow: 2px 2px 0 var(--black);
}

/* ── MESSAGE GROUPS ── */
.nb-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 12px;
    animation: msgIn 0.35s cubic-bezier(0.16,1,0.3,1) both;
}
@keyframes msgIn {
    from { transform: translateY(10px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}
.nb-group.user { align-items: flex-end; }
.nb-group.bot  { align-items: flex-start; }

.nb-sender {
    font-size: 9px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--black); opacity: 0.38; margin-bottom: 5px;
}

/* USER BUBBLE */
.nb-bubble-user {
    background: var(--user-bg);
    color: var(--black);
    border: 2.5px solid var(--border);
    box-shadow: var(--shadow);
    padding: 11px 15px;
    font-size: 13px;
    line-height: 1.6;
    word-break: break-word;
    max-width: 75%;
}

/* ── DIVIDER ── */
.nb-divider {
    text-align: center; font-size: 9px;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--black); opacity: 0.18;
    margin: 4px 0 14px;
}

/* ── TYPING DOTS ── */
.nb-typing {
    background: var(--bot-bg);
    border: 2.5px solid var(--border);
    box-shadow: var(--shadow);
    display: flex; align-items: center; gap: 5px;
    padding: 12px 16px;
    width: fit-content;
}
.nb-typing span {
    width: 7px; height: 7px;
    background: var(--red); border-radius: 50%;
    animation: bounce 1.1s ease-in-out infinite;
}
.nb-typing span:nth-child(2) { animation-delay: 0.18s; }
.nb-typing span:nth-child(3) { animation-delay: 0.36s; }
@keyframes bounce {
    0%,80%,100% { transform: translateY(0); }
    40%          { transform: translateY(-6px); }
}

/* ── BOT BUBBLE ── */
.nb-bubble-bot {
    background: var(--bot-bg);
    color: var(--black);
    border: 2.5px solid var(--border);
    box-shadow: var(--shadow);
    padding: 11px 15px;
    font-size: 13px;
    line-height: 1.6;
    word-break: break-word;
    max-width: 75%;
    font-family: 'Space Mono', monospace;
}
.nb-bubble-bot p { margin: 0 0 8px 0; }
.nb-bubble-bot p:last-child { margin-bottom: 0; }
.nb-bubble-bot strong { color: #7B3FF2; }
.nb-bubble-bot em { font-style: italic; opacity: 0.85; }
.nb-bubble-bot code {
    background: #EDE8FF; color: #5500CC;
    padding: 1px 5px; font-size: 12px;
    border: 1px solid #C4AAFF;
}
.nb-bubble-bot ul, .nb-bubble-bot ol { padding-left: 18px; margin: 6px 0; }
.nb-bubble-bot li { margin-bottom: 3px; font-size: 13px; }
.nb-bubble-bot table {
    border-collapse: collapse; width: 100%;
    margin: 10px 0; font-size: 12px;
}
.nb-bubble-bot th {
    background: var(--lavender); color: var(--black);
    padding: 6px 10px; border: 2px solid var(--border); text-align: left;
    font-family: 'Syne', sans-serif;
}
.nb-bubble-bot td {
    padding: 5px 10px; border: 1.5px solid #ccc; background: #fff;
}
.nb-bubble-bot h1, .nb-bubble-bot h2, .nb-bubble-bot h3 {
    font-family: 'Syne', sans-serif; font-size: 14px;
    margin: 8px 0 4px; color: var(--black);
}

/* ── FIXED INPUT BAR ── */
[data-testid="stChatInput"],
.stChatInputContainer {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 100% !important;
    max-width: 760px !important;
    background: var(--bg) !important;
    padding: 12px 20px 14px !important;
    z-index: 9999 !important;
    margin: 0 !important;
}

[data-testid="stChatInput"] textarea {
    background: #fff !important;
    color: var(--black) !important;
    border: 2px solid var(--border) !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    padding: 10px 14px !important;
    caret-color: var(--red) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--red) !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #aaa !important;
    font-size: 11px !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stChatInput"] button,
[data-testid="stChatInputSubmitButton"] {
    background: var(--red) !important;
    border: 2px solid #FFF8F0 !important;
    border-radius: 0 !important;
    color: var(--black) !important;
    transition: all 0.12s !important;
}
[data-testid="stChatInput"] button:hover,
[data-testid="stChatInputSubmitButton"]:hover {
    background: var(--yellow) !important;
    transform: translate(-1px,-1px) !important;
    box-shadow: 2px 2px 0 #FFF8F0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ───────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_session"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── HEADER ──────────────────────────────────────────────────────
st.markdown("""
<div class="nb-header">
    <div class="nb-logo">🩺</div>
    <div>
        <div class="nb-title">HealthBot</div>
        <div class="nb-subtitle">AI Medical Assistant</div>
    </div>
    <div class="nb-status">
        <div class="nb-dot"></div>Online
    </div>
</div>
""", unsafe_allow_html=True)

# ─── CHAT AREA ───────────────────────────────────────────────────
st.markdown('<div class="nb-chat">', unsafe_allow_html=True)

# Welcome card on first load
if not st.session_state.messages:
    st.markdown("""
    <div class="nb-welcome">
        <div class="nb-welcome-title">👋 Hey there!</div>
        <div class="nb-welcome-text">
            I'm your AI health assistant. Ask me about symptoms, medications,
            nutrition, mental health, or general wellness. I'm here to help.<br><br>
            <strong>Not a substitute for professional medical advice.</strong>
        </div>
        <div class="nb-tags">
            <span class="nb-tag">💊 Medications</span>
            <span class="nb-tag">🤒 Symptoms</span>
            <span class="nb-tag">🥗 Nutrition</span>
            <span class="nb-tag">🧠 Mental Health</span>
            <span class="nb-tag">🏃 Fitness</span>
            <span class="nb-tag">😴 Sleep</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render message history
for i, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        st.markdown(f"""
        <div class="nb-group user">
            <div class="nb-sender">You</div>
            <div class="nb-bubble-user">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Bot bubble: convert markdown to HTML (with table support) then inject
        html_content = markdown.markdown(content, extensions=["tables", "fenced_code"])

        st.markdown(f"""
        <div class="nb-group bot">
            <div class="nb-sender">HealthBot</div>
            <div class="nb-bubble-bot">{html_content}</div>
        </div>
        """, unsafe_allow_html=True)

    if role == "assistant" and i < len(st.session_state.messages) - 1:
        st.markdown('<div class="nb-divider">· · ·</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── CHAT INPUT ──────────────────────────────────────────────────
user_input = st.chat_input("Ask a health question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.pending_query = user_input
    st.rerun()

# ─── HANDLE PENDING QUERY ────────────────────────────────────────
if "pending_query" in st.session_state:
    user_input = st.session_state.pending_query
    del st.session_state.pending_query

    typing_ph = st.empty()
    typing_ph.markdown("""
    <div style="padding: 0 20px;">
        <div class="nb-group bot">
            <div class="nb-sender">HealthBot</div>
            <div class="nb-typing"><span></span><span></span><span></span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        res = requests.post(
            "http://localhost:8000/api/chat",
            json={"message": user_input, "session_id": st.session_state.session_id},
            timeout=30
        )
        data = res.json()
        bot_response = data.get("response", "No response received.")
    except Exception:
        bot_response = "⚠️ **Connection error.** Could not reach the backend. Please make sure the server is running on `localhost:8000`."

    typing_ph.empty()
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()