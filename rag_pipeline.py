import os
import streamlit as st

from dotenv import load_dotenv

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_community.vectorstores import (
    FAISS
)

from langchain_groq import ChatGroq

# =========================
# Load Environment Variables
# =========================

load_dotenv()

# =========================
# Cached Embedding Model
# =========================

@st.cache_resource
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

embeddings = get_embeddings()

# =========================
# Groq LLM
# =========================

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

# =========================
# Split Documents
# =========================

def split_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = text_splitter.split_documents(
        documents
    )

    return split_docs

# =========================
# Create Vectorstore
# =========================

def create_vectorstore(documents, repo_name):

    split_docs = split_documents(
        documents
    )

    vectorstore = FAISS.from_documents(
        documents=split_docs,
        embedding=embeddings
    )

    vectorstore_path = (
        f"vectorstores/{repo_name}"
    )

    vectorstore.save_local(
        vectorstore_path
    )

    return vectorstore

# =========================
# Cached Vectorstore Loader
# =========================

@st.cache_resource
def load_vectorstore(repo_name):

    vectorstore_path = (
        f"vectorstores/{repo_name}"
    )

    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore

# =========================
# Ask Question
# =========================

def ask_question(vectorstore, question):

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    docs = retriever.invoke(
        question
    )

    context = ""

    citations = ""

    for doc in docs:

        context += (
            doc.page_content + "\n\n"
        )

        citations += f"""
📦 Repository: {doc.metadata.get('repo_name', 'Unknown')}
📄 File: {doc.metadata.get('file_name', 'Unknown')}
📁 Path: {doc.metadata.get('file_path', 'Unknown')}

"""

    prompt = f"""
You are an AI GitHub Repository Assistant.

Use ONLY the provided repository context.

If answer is not found in context, say exactly:
"I could not find relevant information in the repository."

Context:
{context}

Question:
{question}

Instructions:
1. Give repository-aware answers
2. Mention file names when relevant
3. Avoid hallucinations
4. Keep answers professional
5. Explain clearly
"""

    response = llm.invoke(
        prompt
    )

    response_text = response.content

    # =========================
    # No Relevant Answer Found
    # =========================

    if (
        "could not find" in response_text.lower()
        or
        "not available" in response_text.lower()
    ):

        final_answer = response_text

    # =========================
    # Relevant Answer Found
    # =========================

    else:

        final_answer = f"""
{response_text}

---
# 📚 Source Citations

{citations}
"""

    return final_answer

# =========================
# Generate Documentation
# =========================

def generate_documentation(vectorstore):

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 8}
    )

    docs = retriever.invoke(
        "Explain the repository architecture and functionality"
    )

    context = ""

    for doc in docs:

        context += (
            doc.page_content + "\n\n"
        )

    prompt = f"""
Generate professional GitHub repository documentation.

Include:
1. Project overview
2. Main functionality
3. Tech stack
4. Important files
5. Architecture summary
6. Workflow explanation
7. Core modules
8. Repository insights

Repository Context:
{context}
"""

    response = llm.invoke(
        prompt
    )

    return response.content