# chunking + embedding + retrieval

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50
    )

    chunks = splitter.create_documents(documents)
    return chunks

def create_vectorstore(chunks):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model
    )

    return vectorstore

def retrieve_context(vectorstore, query):
    docs = vectorstore.similarity_search(query, k=3)

    return "\n".join([doc.page_content for doc in docs])