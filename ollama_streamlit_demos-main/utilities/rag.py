import chromadb
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader



DB_PATH = "./cybersecurity_db"
#embedder = SentenceTransformer("all-MiniLM-L6-v2")
embedding_model = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
# embedding_model = HuggingFaceEmbeddings(
#     model_name="nomic-ai/nomic-embed-text-v2-moe",
#     model_kwargs={"trust_remote_code": True}  # ✅ Allows loading the model safely
# )
#chroma_client = chromadb.PersistentClient(path="./cybersecurity_db")
#collection = chroma_client.get_or_create_collection(name="cybersecurity_docs")
vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)
global text


def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

"""
def index_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    sentences = text.split("\n")
    
    pdf_id_prefix = pdf_path.replace(" ", "_")  # Normalize filename
    existing_ids = {item["id"] for item in collection.get()["metadatas"]}  # Get stored IDs

    embeddings = embedder.encode(sentences).tolist()

    new_data = []
    for i, sentence in enumerate(sentences):
        unique_id = f"{pdf_id_prefix}_{i}"
        
        # Only add if the ID is not already stored
        if unique_id not in existing_ids:
            new_data.append(
                {
                    "id": unique_id,
                    "embedding": embeddings[i],
                    "metadata": {"text": sentence}
                }
            )

    if new_data:
        collection.add(
            ids=[item["id"] for item in new_data],
            embeddings=[item["embedding"] for item in new_data],
            metadatas=[item["metadata"] for item in new_data],
        )
        print(f"Indexed {len(new_data)} new entries from {pdf_path}")
    else:
        print(f"Skipped indexing for {pdf_path}, as all entries already exist.")
"""



def index_pdf(pdf_path):
    """Indexes cybersecurity PDFs into the vector store without skipping new documents."""
    global vector_store

    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()

    # Increase chunk size to keep more context together
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=300)
    docs = text_splitter.split_documents(documents)

    # Fetch existing document IDs safely
    existing_metadatas = vector_store.get()["metadatas"]
    existing_ids = set(m["source"] for m in existing_metadatas if "source" in m)  # ✅ Extract unique IDs

    new_data = []
    for i, doc in enumerate(docs):
        doc_id = f"{pdf_path}_{i}"  # Generate unique ID for each document

        if doc_id not in existing_ids:  # ✅ Only add if this specific chunk is new
            doc.metadata["source"] = doc_id  # ✅ Add unique ID to metadata
            new_data.append(doc)


    if new_data:
        vector_store.add_documents(new_data)  # ✅ Add only new documents
        vector_store.persist()
        print(f"Indexed {len(new_data)} new chunks from {pdf_path}")
    else:
        print(f"Skipped indexing for {pdf_path}, as all chunks already exist.")

# def retrieve_context(query, k=3):
#     """Retrieves a limited number of relevant chunks and filters results."""
#     global vector_store

#     retriever = vector_store.as_retriever(
#         search_type="mmr",  # Maximal Marginal Relevance to increase diversity
#         search_kwargs={"k": k, "fetch_k": 5}  # Fetch 5, but only return 3
#     )

#     docs = retriever.get_relevant_documents(query)

#     if not docs:
#         return "No relevant cybersecurity information found."

#     # Convert query into a set of words
#     query_words = set(query.lower().split())

#     # Score each chunk based on word overlap with query
#     scored_chunks = []
#     for doc in docs:
#         chunk_words = set(doc.page_content.lower().split())
#         match_count = len(query_words.intersection(chunk_words))  # Count matching words
#         scored_chunks.append((doc.page_content, match_count))

#     # Sort by highest match count and take the top 2
#     scored_chunks.sort(key=lambda x: x[1], reverse=True)
#     top_chunks = [chunk[0] for chunk in scored_chunks[:2]]  # ✅ Only keep top 2 relevant chunks

#     return "\n".join(top_chunks) if top_chunks else "No highly relevant cybersecurity information found."



def retrieve_context(query, k=5):
    """Retrieves relevant chunks using LangChain's retriever and filters results."""
    global vector_store

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 10}
    )

    docs = retriever.get_relevant_documents(query)

    if not docs:
        return "No relevant cybersecurity information found."

    # Filter chunks: Keep only those containing the most keywords from the query
    query_words = set(query.lower().split())  # Convert query to set of words
    filtered_docs = []
    
    for doc in docs:
        chunk_words = set(doc.page_content.lower().split())
        match_count = len(query_words.intersection(chunk_words))  # Count word matches
        
        # Keep only chunks that share at least 30% of words with the query
        if match_count / len(query_words) >= 0.3:
            filtered_docs.append(doc.page_content)

    if filtered_docs:
        return "\n".join(filtered_docs)
    
    return "No highly relevant cybersecurity information found."






# Example: Index a document
index_pdf("./cybersecurity_basics.pdf")