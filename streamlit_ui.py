import streamlit as st
import requests

st.set_page_config(page_title="Health Chatbot", layout="centered")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}
[data-testid="stDeployButton"] {display: none;}

.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.title {
    text-align: center;
    font-size: 36px;
    font-weight: 600;
    font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", sans-serif;
    color: #f5f5f7;
    margin-top: 1px;
    margin-bottom: 1px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>Health Chatbot</div>", unsafe_allow_html=True)

# ------------------ STYLE ------------------
st.markdown("""
<style>

/* USER MESSAGE → RIGHT */
.user-msg {
    background-color: #2563eb;
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 0;
    margin-left: auto;
    width: fit-content;
    max-width: 70%;
}

/* BOT MESSAGE → LEFT */
.bot-msg {
    background-color: #1e1e1e;
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 0;
    width: fit-content;
    max-width: 70%;
}

/* CONTAINER FIX */
.chat-container {
    display: flex;
    flex-direction: column;

}

</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_session"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>", unsafe_allow_html=True)
        st.markdown(msg["content"])  # supports tables
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------ INPUT ------------------
user_input = st.chat_input("Ask something...")

if user_input:
    # store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # store pending query
    st.session_state.pending_query = user_input

    st.rerun()

# ------------------ HANDLE PENDING QUERY ------------------
if "pending_query" in st.session_state:
    user_input = st.session_state.pending_query
    del st.session_state.pending_query

    with st.spinner("Thinking..."):
        try:
            res = requests.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": user_input,
                    "session_id": st.session_state.session_id
                }
            )

            data = res.json()
            bot_response = data.get("response", "No response")

        except:
            bot_response = "Error connecting to backend"

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response
    })

    st.rerun()