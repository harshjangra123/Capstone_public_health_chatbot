import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.embeddings import embedding_model


DATA_FOLDER = r"C:\Users\harsh\Desktop\capstone_implementation\data"
PERSIST_DIR = r"C:\Users\harsh\Desktop\capstone_implementation\csv_vector_db"


def csv_to_documents(file_path):
    df = pd.read_csv(file_path)

    documents = []

    for _, row in df.iterrows():
        parts = []

        for col, val in row.items():
            if pd.isna(val):
                continue

            col = col.replace("_", " ")
            parts.append(f"{col} {val}")

        if not parts:
            continue

        text = ", ".join(parts)

        metadata = {
            "source_file": os.path.basename(file_path),
            "dataset": os.path.basename(file_path).replace(".csv", "")
        }

        documents.append(Document(page_content=text, metadata=metadata))

    return documents


def ingest_all_csvs():
    all_docs = []

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".csv"):
            file_path = os.path.join(DATA_FOLDER, file)

            print(f"📄 Processing: {file}")

            docs = csv_to_documents(file_path)
            all_docs.extend(docs)

    print(f"Total documents: {len(all_docs)}")

    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding_model,
        persist_directory=PERSIST_DIR
    )

    vectorstore.persist()

    print("✅ Vector DB created successfully!")


if __name__ == "__main__":
    ingest_all_csvs()