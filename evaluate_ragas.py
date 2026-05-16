from datasets import Dataset

from ragas import evaluate

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

from rag_pipeline import (
    load_vectorstore,
    ask_question
)

# =========================
# Select Repository
# =========================

repo_name = input(
    "Enter repository name: "
)

# =========================
# Load Vectorstore
# =========================

print("\nLoading vectorstore...\n")

vectorstore = load_vectorstore(
    repo_name
)

# =========================
# Ask Question
# =========================

question = input(
    "\nEnter your question: "
)

# =========================
# Generate Answer
# =========================

print("\nGenerating answer...\n")

answer = ask_question(
    vectorstore,
    question
)

print("\nGenerated Answer:\n")

print(answer)

# =========================
# Retrieve Contexts
# =========================

docs = vectorstore.similarity_search(
    question,
    k=4
)

contexts = [

    doc.page_content

    for doc in docs
]

# =========================
# Create Dataset
# =========================

data = {

    "question": [
        question
    ],

    "answer": [
        answer
    ],

    "contexts": [
        contexts
    ]

}

dataset = Dataset.from_dict(data)

# =========================
# Run RAGAS Evaluation
# =========================

print("\nRunning RAGAS Evaluation...\n")

result = evaluate(

    dataset,

    metrics=[

        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall

    ]

)

# =========================
# Print Results
# =========================

print("\nRAGAS Evaluation Results:\n")

print(result)