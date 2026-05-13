import os
from langchain_core.documents import Document
SUPPORTED_EXTENSIONS = [
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
]

def load_repository(repo_path, repo_name):

    documents = []

    for root, dirs, files in os.walk(repo_path):

        # Ignore unnecessary folders
        dirs[:] = [
            d for d in dirs
            if d not in [".git", "node_modules", "venv", "__pycache__"]
        ]

        for file in files:

            extension = os.path.splitext(file)[1]

            # Skip unsupported files
            if extension not in SUPPORTED_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)

            try:

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                relative_path = os.path.relpath(file_path, repo_path)

                document = Document(
                    page_content=content,
                    metadata={
                        "repo_name": repo_name,
                        "file_name": file,
                        "file_path": relative_path,
                        "language": extension,
                    }
                )

                documents.append(document)

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return documents