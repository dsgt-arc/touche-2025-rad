import pandas as pd
from pathlib import Path
from tqdm import tqdm
import chromadb


def test_embeddings(
    parquet_dir: str, chroma_client: chromadb.Client, collection_name: str
):
    """Load embeddings from parquet files into ChromaDB.

    Args:
        parquet_dir: Directory containing parquet files
        chroma_client: ChromaDB client instance
        collection_name: Name of the collection to store embeddings
    """
    parquet_files = list(Path(parquet_dir).glob("*.parquet"))
    print(f"Found {len(parquet_files)} parquet files")

    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Debate arguments and their embeddings"},
    )

    for parquet_path in tqdm(parquet_files, desc="Loading embeddings"):
        df = pd.read_parquet(parquet_path)

        if df.empty:
            print(f"Skipping empty file: {parquet_path.name}")
            continue

        # Print the DataFrame structure for debugging
        print(f"\nDataFrame from {parquet_path.name}:")
        print(df.head())  # Check the first few rows

        # Print first few embeddings for debugging
        print(f"\nFirst few embeddings from {parquet_path.name}:")
        for i, embedding in enumerate(df["embedding"].head(5)):
            print(f"Embedding {i + 1}: {embedding[:5]}")  # Print first 5 dimensions

        # Ensure embeddings are in the correct format
        embeddings = [list(embedding) for embedding in df["embedding"]]
        print(f"Type of embeddings: {type(embeddings)}")
        print(
            f"First embedding: {embeddings[0][:5]}"
        )  # Print first 5 dimensions of the first embedding

        collection.add(
            documents=df["text"].tolist(),
            embeddings=embeddings,  # Ensure this is a list of lists
            ids=df["id"].tolist(),
            metadatas=[
                {
                    "topic_id": row["topic_id"],
                    "topic": row["topic"],
                    "is_chunk": True,
                    "num_sentences": row["num_sentences"],
                }
                for _, row in df.iterrows()
            ],
        )
        print(f"Loaded {len(df)} embeddings from {parquet_path.name}")


chroma_client = chromadb.PersistentClient(path="../chroma_db")

if __name__ == "__main__":
    test_embeddings("../embedded_data", chroma_client, "debate_arguments")
