import chromadb
import fitz  # PyMuPDF
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Directory for the vector store database
DB_PATH = "./cybersecurity_db"

# Use a lightweight embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def index_data(file_path):
    """Indexes both PDFs and JSON files into the vector store."""
    documents = []

    if file_path.endswith(".pdf"):
        # Handle PDF Files
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])
        documents.append(Document(page_content=text, metadata={"source": file_path}))

    elif file_path.endswith(".json"):
        # Handle JSON Files
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Expecting a key "scenarios" with a list of scenario dictionaries
        if "scenarios" in json_data and isinstance(json_data["scenarios"], list):
            for scenario in json_data["scenarios"]:
                title = scenario.get("title", "No Title")
                description = scenario.get("description", "")
                tasks = " ".join(scenario.get("tasks", []))
                solution = scenario.get("solution", "")
                learning_objectives = " ".join(scenario.get("learning_objectives", []))

                combined_text = (
                    f"Scenario: {title}\n\n"
                    f"Description: {description}\n\n"
                    f"Tasks: {tasks}\n\n"
                    f"Solution: {solution}\n\n"
                    f"Learning Objectives: {learning_objectives}"
                )
                documents.append(Document(page_content=combined_text, metadata={"source": file_path}))
    else:
        print(f"⚠️ Unsupported file type: {file_path}")
        return

    # Use chunking to preserve context in manageable pieces
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=300)
    docs = text_splitter.split_documents(documents)

    # Avoid indexing duplicate data: we use a unique id per chunk.
    existing_metadatas = vector_store.get()["metadatas"]
    existing_ids = set(m["source"] for m in existing_metadatas if "source" in m)

    new_data = []
    for i, doc in enumerate(docs):
        doc_id = f"{file_path}_{i}"  # Unique ID for each chunk
        if doc_id not in existing_ids:
            doc.metadata["source"] = doc_id
            new_data.append(doc)

    if new_data:
        vector_store.add_documents(new_data)
        vector_store.persist()
        print(f"✅ Indexed {len(new_data)} new chunks from {file_path}")
    else:
        print(f"⚠️ Skipped indexing for {file_path}, as all chunks already exist.")

def retrieve_context(query, k=5):
    """
    Retrieves relevant text chunks from the vector store using Maximal Marginal Relevance (MMR)
    and filters the results to ensure high overlap with the query.
    """
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 10}
    )

    docs = retriever.get_relevant_documents(query)
    if not docs:
        return "No relevant cybersecurity information found."

    query_words = set(query.lower().split())
    filtered_docs = []
    for doc in docs:
        chunk_words = set(doc.page_content.lower().split())
        match_count = len(query_words.intersection(chunk_words))
        if match_count / len(query_words) >= 0.3:
            filtered_docs.append(doc.page_content)

    if filtered_docs:
        return "\n".join(filtered_docs)
    
    return "No highly relevant cybersecurity information found."

# -----------------------------
# Index documents (run once or as needed)
# -----------------------------
# Uncomment or add additional files as necessary.
#index_data("./Petra_logistics.pdf")  # Example PDF
index_data("./CybersecurityScenarios.json")
