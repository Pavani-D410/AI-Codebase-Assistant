import os
import streamlit as st

from github_loader import load_repository

from rag_pipeline import (
    create_vectorstore,
    load_vectorstore,
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
    '<div class="main-title">🚀 RepoSage</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered GitHub Repository Intelligence Assistant</div>',
    unsafe_allow_html=True
)

# =========================
# Repository URL Input
# =========================

repo_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/user/repository"
)

# =========================
# Buttons
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

            try:

                # Extract repository name
                repo_name = repo_url.split("/")[-1]

                # Local repository path
                repo_path = f"repos/{repo_name}"

                # Clone only if repository does not exist
                if not os.path.exists(repo_path):

                    os.system(
                        f"git clone {repo_url} {repo_path}"
                    )

                # Load repository documents
                documents = load_repository(
                    repo_path,
                    repo_name
                )

                # Create vectorstore
                create_vectorstore(
                    documents,
                    repo_name
                )

                st.success(
                    f"{repo_name} processed successfully!"
                )

            except Exception as e:

                st.error(
                    f"Error processing repository: {e}"
                )

# =========================
# Repository Selector
# =========================

available_repos = []

if os.path.exists("vectorstores"):

    available_repos = os.listdir(
        "vectorstores"
    )

# Add placeholder option
repo_options = (
    ["-- Select Repository --"]
    + available_repos
)

selected_repo = st.selectbox(
    "Select Repository",
    repo_options
)

# Prevent automatic selection
if selected_repo == "-- Select Repository --":

    selected_repo = None

# =========================
# Generate Documentation
# =========================

if doc_clicked and selected_repo:

    with st.spinner(
        "Generating documentation..."
    ):

        try:

            vectorstore = load_vectorstore(
                selected_repo
            )

            docs = generate_documentation(
                vectorstore
            )

            st.markdown("---")

            st.subheader(
                "📘 Repository Documentation"
            )

            st.markdown(docs)

        except Exception as e:

            st.error(
                f"Documentation Error: {e}"
            )

# =========================
# Workflow
# =========================

st.markdown(
    """
✓ Enter Repository URL  
✓ Process Repository  
✓ Select Repository  
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

if question and selected_repo:

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                # Load selected vectorstore
                vectorstore = load_vectorstore(
                    selected_repo
                )

                # Ask question
                answer = ask_question(
                    vectorstore,
                    question
                )

                st.markdown(answer)

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

# =========================
# No Repository Selected
# =========================

if not selected_repo:

    st.info(
        "Please select a repository to start querying."
    )