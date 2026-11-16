from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash-lite"
SYSTEM_INSTRUCTION = """
Answer from the given manual.
If the answer is not available say: Info not available
Give simple and clear answers
"""

st.set_page_config(page_title="Trading Knowledge Chatbot", page_icon="📈")


@st.cache_resource
def get_client() -> genai.Client:
    # Key is read from .streamlit/secrets.toml
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


@st.cache_data
def load_manual() -> str:
    return (Path(__file__).parent / "knowledge_base.md").read_text(encoding="utf-8")


def ask_gemini(question: str) -> str:
    response = get_client().models.generate_content(
        model=MODEL,
        contents=load_manual() + "\n\nQuestion: " + question,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    return response.text or "Info not available"


# ---------- UI ----------
st.title("📈 Trading Knowledge Chatbot")
st.caption("Answers come only from the built-in trading knowledge base. Educational use only, not financial advice.")

with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask your trading question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_gemini(question)
            except Exception as e:
                answer = f"⚠️ Error: {e}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
