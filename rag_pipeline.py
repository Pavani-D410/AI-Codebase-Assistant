import os

from git import Repo

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_groq import ChatGroq

from langchain_core.documents import Document


load_dotenv()


# =========================
# Embeddings Model
# =========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================
# Groq LLM
# =========================

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile"
)


# =========================
# Clone GitHub Repository
# =========================

def clone_repo(repo_url):

    repo_name = repo_url.split("/")[-1]

    local_path = f"repos/{repo_name}"


    if not os.path.exists(local_path):

        Repo.clone_from(repo_url, local_path)

    return local_path


# =========================
# Load Source Code Files
# =========================

def load_code_files(repo_path):

    documents = []


    allowed_extensions = [

        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".swift",
        ".kt",
        ".scala",
        ".dart",
        ".sh",
        ".bash",
        ".zsh",
        ".sql",
        ".html",
        ".css",
        ".scss",
        ".sass",
        ".vue",
        ".svelte",
        ".xml",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".md",
        ".txt",
        ".rst",
        ".tf",
        ".graphql",
        ".gql"
    ]


    for root, dirs, files in os.walk(repo_path):

        # Ignore unnecessary folders
        dirs[:] = [

            d for d in dirs

            if d not in [

                ".git",
                "node_modules",
                "venv",
                "__pycache__",
                "dist",
                "build",
                ".next",
                ".idea",
                ".vscode",
                "coverage",
                "target",
                "bin",
                "obj",
                ".dart_tool",
                ".gradle",
                ".terraform"
            ]
        ]


        for file in files:

            if any(
                file.endswith(ext)
                for ext in allowed_extensions
            ):

                file_path = os.path.join(root, file)

                try:

                    # Skip huge files
                    if (
                        os.path.getsize(file_path)
                        > 1_000_000
                    ):
                        continue


                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        code = f.read()

                        documents.append(
                            Document(
                                page_content=code,
                                metadata={
                                    "source": file_path
                                }
                            )
                        )

                except:

                    pass


    return documents


# =========================
# Create Vector Database
# =========================

def create_vectorstore(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)


    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vectorstore


# =========================
# Process Repository
# =========================

def process_repository(repo_url):

    repo_name = repo_url.split("/")[-1]

    vector_path = f"vectorstore/{repo_name}"


    # =========================
    # Load Existing Vector DB
    # =========================

    if os.path.exists(vector_path):

        vectorstore = FAISS.load_local(
            vector_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        return vectorstore


    # =========================
    # Clone Repo
    # =========================

    repo_path = clone_repo(repo_url)


    # =========================
    # Load Code Files
    # =========================

    docs = load_code_files(repo_path)


    # =========================
    # Create Vector DB
    # =========================

    vectorstore = create_vectorstore(docs)


    # =========================
    # Save Vector DB
    # =========================

    vectorstore.save_local(vector_path)


    return vectorstore


# =========================
# Ask Questions
# =========================

def ask_question(vectorstore, question):

    docs_with_scores = (
        vectorstore.similarity_search_with_score(
            question,
            k=4
        )
    )


    # No docs
    if not docs_with_scores:

        return (
            "No relevant repository "
            "information found."
        )


    # Hallucination reduction
    best_score = docs_with_scores[0][1]


    if best_score > 1.5:

        return (
            "This question appears unrelated "
            "to the repository.\n\n"
            "Please ask repository-specific questions."
        )


    docs = [
        doc for doc, score in docs_with_scores
    ]


    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )


    prompt = f"""
You are an AI Code Documentation Assistant.

Answer ONLY using repository context.

If answer is unavailable,
say:
'I could not find relevant information.'

Explain clearly and professionally.

Context:
{context}

Question:
{question}
"""


    response = llm.invoke(prompt)

    return response.content


# =========================
# Generate Documentation
# =========================

def generate_documentation(vectorstore):

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 10}
    )

    docs = retriever.invoke(
        "Explain the overall repository"
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )


    prompt = f"""
You are an expert software architect.

Analyze the repository carefully.

Generate:

1. Project Overview
2. Main Features
3. Technologies Used
4. Architecture Explanation
5. Folder Structure Summary
6. Setup Instructions
7. Important Components

Explain professionally and clearly.

Context:
{context}
"""


    response = llm.invoke(prompt)

    return response.content