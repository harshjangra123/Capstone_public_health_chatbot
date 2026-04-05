from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.embeddings import embedding_model

def load_registry_index():
    vectorstore = Chroma(
        persist_directory="chroma_registry_db",
        embedding_function=embedding_model
    )

    return vectorstore

vectorstore = load_registry_index()

def get_best_dataset(query: str):
    # search most similar dataset
    # use similarity score
    docs = vectorstore.similarity_search_with_score(query, k=1)

    best_doc, score = docs[0]

    print("Query:", query)
    print("Matched text:", best_doc.page_content)
    print("Metadata:", best_doc.metadata)
    print("Similarity Score:", score)

    # threshold check (IMPORTANT)
    if score > 2.0: 
        print("No good dataset match found")
        return None

    return best_doc.metadata["resource_id"]


# if __name__ == "__main__":
#     query = "HIV cases in India and how can we avoid it"
#     dataset_id = get_best_dataset(query)
#     print("Selected dataset:", dataset_id)