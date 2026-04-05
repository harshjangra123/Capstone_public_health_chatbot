import json
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_registry_index():
    
    # 1. Load registry
    with open("app\datasets.json", "r") as f:
        registry = json.load(f)

    # 2. Initialize embedding model (LOCAL)
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    texts = []
    metadatas = []

    # 3. Convert registry → text
    for item in registry:
        text = f"""
        Title: {item['title']}
        Description: {item['description']}
        Keywords: {", ".join(item['keywords'])}
        Category: {item['category']}
        """

        texts.append(text)

        metadatas.append({
            "resource_id": item["resource_id"],
            "title": item["title"],
            "category": item["category"]
        })

    # 4. Create vector DB
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        persist_directory="chroma_registry_db"
    )

    # 5. Save to disk
    vectorstore.persist()

    print("✅ Registry index created using local embeddings!")

build_registry_index()