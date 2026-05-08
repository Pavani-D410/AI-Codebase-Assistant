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
# Header
# =========================

st.title("💻 CodeRAG AI")

st.markdown(
    "AI-powered GitHub Repository Assistant"
)


# =========================
# Repository Input
# =========================

repo_url = st.text_input(
    "Enter GitHub Repository URL"
)


# =========================
# Session State
# =========================

if "vectorstore" not in st.session_state:

    st.session_state.vectorstore = None


# =========================
# Process Repository
# =========================

if st.button("Process Repository"):

    with st.spinner("Processing repository..."):

        vectorstore = process_repository(repo_url)

        st.session_state.vectorstore = vectorstore

        st.success(
            "Repository processed successfully!"
        )


# =========================
# Documentation Generator
# =========================

if st.session_state.vectorstore:

    if st.button("Generate Documentation"):

        with st.spinner(
            "Generating documentation..."
        ):

            docs = generate_documentation(
                st.session_state.vectorstore
            )

            st.subheader(
                "📘 Repository Documentation"
            )

            st.markdown(docs)


# =========================
# Chatbot Questions
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