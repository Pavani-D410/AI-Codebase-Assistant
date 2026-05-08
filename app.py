import streamlit as st

from rag_pipeline import (
    process_repository,
    ask_question,
    generate_documentation
)

# =========================
# Page Config
# =========================

st.set_page_config(
    page_title="CodeRAG AI",
    page_icon="💻",
    layout="wide"
)

# =========================
# Clean UI CSS
# =========================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #F8FAFC;
    }

    .main .block-container {
        max-width: 1100px;
        margin: auto;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #6B7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
        padding: 10px !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        background-color: #2563EB;
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.6rem;
    }

    .stButton > button:hover {
        background-color: #1D4ED8;
        color: white;
    }

    .stChatInput textarea {
        font-size: 15px !important;
        min-height: 80px !important;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Header
# =========================

st.markdown(
    '<div class="main-title">💻 CodeRAG AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered GitHub Repository Assistant</div>',
    unsafe_allow_html=True
)

# =========================
# Repository URL
# =========================

repo_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/user/repository"
)

# =========================
# Session State
# =========================

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# =========================
# Buttons Row
# =========================

col1, col2 = st.columns(2)

with col1:

    process_clicked = st.button(
        "Process Repository"
    )

with col2:

    doc_clicked = st.button(
        "Generate Documentation"
    )

# =========================
# Process Repository
# =========================

if process_clicked:

    if repo_url.strip() == "":

        st.warning(
            "Please enter a repository URL."
        )

    else:

        with st.spinner(
            "Processing repository..."
        ):

            vectorstore = process_repository(
                repo_url
            )

            st.session_state.vectorstore = (
                vectorstore
            )

            st.success(
                "Repository processed successfully!"
            )

# =========================
# Generate Documentation
# =========================

if doc_clicked:

    if st.session_state.vectorstore:

        with st.spinner(
            "Generating documentation..."
        ):

            docs = generate_documentation(
                st.session_state.vectorstore
            )

            st.markdown("---")

            st.subheader(
                "📘 Repository Documentation"
            )

            st.markdown(docs)

# =========================
# Workflow
# =========================

st.markdown(
    """
✓ Enter Repository URL  
✓ Process Repository  
✓ Generate Documentation  
✓ Ask Questions
"""
)

# =========================
# Chat Section
# =========================

question = st.chat_input(
    "Ask questions about the repository..."
)

if question and st.session_state.vectorstore:

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_question(
                st.session_state.vectorstore,
                question
            )

            st.markdown(answer)