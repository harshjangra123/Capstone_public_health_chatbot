from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_registry_index():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory="chroma_registry_db",
        embedding_function=embedding_model
    )

    return vectorstore


def get_best_dataset(query: str):
    vectorstore = load_registry_index()

    # search most similar dataset
    docs = vectorstore.similarity_search(query, k=1)

    best_doc = docs[0]

    # DEBUG (very useful)
    print("Query:", query)
    print("Matched text:", best_doc.page_content)
    print("Metadata:", best_doc.metadata)

    return best_doc.metadata["resource_id"]


# if __name__ == "__main__":
#     query = "HIV cases in India and how can we avoid it"
#     dataset_id = get_best_dataset(query)
#     print("Selected dataset:", dataset_id)