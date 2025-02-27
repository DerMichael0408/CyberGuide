import chromadb
import fitz  # PyMuPDF
import json
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema import Document



DB_PATH = "./cybersecurity_db"
embedding_model = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)
global text


def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def index_data(file_path):
    """Indexes both PDFs and JSON files into the vector store."""
    global vector_store

    documents = []

    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])
        documents.append(Document(page_content=text, metadata={"source": file_path}))

    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        if "scenarios" in json_data and isinstance(json_data["scenarios"], list):
            for scenario in json_data["scenarios"]:
                title = scenario.get("title", "No Title")
                description = scenario.get("description", "")
                tasks = " ".join(scenario.get("tasks", []))
                solution = scenario.get("solution", "")
                learning_objectives = " ".join(scenario.get("learning_objectives", []))

                combined_text = f"Scenario: {title}\n\nDescription: {description}\n\nTasks: {tasks}\n\nSolution: {solution}\n\nLearning Objectives: {learning_objectives}"
                
                documents.append(Document(page_content=combined_text, metadata={"source": file_path}))

    else:
        print(f"⚠️ Unsupported file type: {file_path}")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=300)
    docs = text_splitter.split_documents(documents)

    existing_metadatas = vector_store.get()["metadatas"]
    existing_ids = set(m["source"] for m in existing_metadatas if "source" in m)

    new_data = []
    for i, doc in enumerate(docs):
        doc_id = f"{file_path}_{i}"  

        if doc_id not in existing_ids:   
            doc.metadata["source"] = doc_id
            new_data.append(doc)

    if new_data:
        vector_store.add_documents(new_data)
        vector_store.persist()
        print(f" Indexed {len(new_data)} new chunks from {file_path}")
    else:
        print(f" Skipped indexing for {file_path}, as all chunks already exist.")





# def retrieve_context(query, k=5):
#     """Retrieves relevant chunks using LangChain's retriever and filters results."""
#     global vector_store

#     retriever = vector_store.as_retriever(
#         search_type="mmr",
#         search_kwargs={"k": k, "fetch_k": 10}
#     )

#     docs = retriever.get_relevant_documents(query)

#     if not docs:
#         return "No relevant cybersecurity information found."

#     # Filter chunks: Keep only those containing the most keywords from the query
#     query_words = set(query.lower().split())  # Convert query to set of words
#     filtered_docs = []
    
#     for doc in docs:
#         chunk_words = set(doc.page_content.lower().split())
#         match_count = len(query_words.intersection(chunk_words))  # Count word matches
        
#         # Keep only chunks that share at least 30% of words with the query
#         if match_count / len(query_words) >= 0.3:
#             filtered_docs.append(doc.page_content)

#     if filtered_docs:
#         return "\n".join(filtered_docs)
    
#     return "No highly relevant cybersecurity information found."

def retrieve_context(query, k=5):
    """Retrieves relevant chunks using LangChain's retriever and filters results."""
    global vector_store

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 10}
    )

    docs = retriever.invoke(query)

    if not docs:
        return "No relevant cybersecurity information found.", []

    # Rank retrieved documents based on keyword overlap with the query
    query_words = set(query.lower().split())
    ranked_docs = sorted(docs, key=lambda doc: len(query_words.intersection(set(doc.page_content.lower().split()))), reverse=True)

    # Most relevant chunk (top-ranked)
    most_relevant_chunk = ranked_docs[0].page_content if ranked_docs else "No highly relevant content found."

    # Return both the most relevant chunk and all retrieved docs
    return most_relevant_chunk, [doc.page_content for doc in ranked_docs]





# Index the documents
index_data("./Petra_logistics.pdf")
index_data("./CybersecurityScenarios.json")