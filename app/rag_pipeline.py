# chunking + embedding + retrieval

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.embeddings import embedding_model

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=30
    )
    return splitter.create_documents(documents)

def create_vectorstore(chunks):
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    return vectorstore

def retrieve_context(vectorstore, query):
    docs = vectorstore.similarity_search(query, k=2)

    context = "\n".join([doc.page_content for doc in docs])

    return context[:1000]