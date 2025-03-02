"""Embedding generation for debate arguments."""

import torch
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from tqdm import tqdm
from sqlalchemy import create_engine, text

from scipy.spatial.distance import cosine


def get_device() -> str:
    """Get the appropriate device for tensor operations."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def print_embedding_info(
    batch_embeddings: np.ndarray, batch: List[str], batch_idx: int
) -> None:
    """Print information about generated embeddings.

    Args:
        batch_embeddings: Numpy array of embeddings for current batch
        batch: List of text chunks in current batch
        batch_idx: Current batch number
    """
    print(f"\nBatch {batch_idx + 1} Embedding Info:")
    print(f"Number of chunks embedded: {len(batch)}")
    print(f"Embedding dimension: {batch_embeddings.shape[1]}")
    print(f"Sample text (first chunk): {batch[0][:100]}...")
    print(f"Sample embedding (first 5 dims): {batch_embeddings[0][:5]}")
    print("-" * 80)


class ArgumentEmbedder:
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        """Initialize the embedding model.

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.device = get_device()
        print(f"Using device: {self.device}")

        self.model = SentenceTransformer(model_name)
        self.model.to(self.device)

    def embed_texts(self, texts: List[str], debug: bool = False) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        batch_size = 32
        embeddings = []
        with tqdm(total=len(texts), desc="Generating embeddings") as pbar:
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = (
                    self.model.encode(
                        batch,
                        convert_to_tensor=True,
                        device=self.device,
                        show_progress_bar=False,
                    )
                    .cpu()
                    .numpy()
                )

                if debug:
                    print_embedding_info(batch_embeddings, batch, i // batch_size)

                embeddings.append(batch_embeddings)
                pbar.update(len(batch))
        return np.vstack(embeddings)

    def embed(self, text: str) -> np.ndarray:
        """Generate embeddings for a single text input."""
        return self.embed_texts([text])


def embed_text(input_text):
    embedder = ArgumentEmbedder()
    return embedder.embed(input_text)


def search_similar_embeddings(embedded_input: np.ndarray):
    # Flatten the NumPy array to a list for the SQL query
    embedded_input = embedded_input.flatten()
    # print(embedded_input)

    # Create engine
    db_url = "postgresql://aaryanpotdar:password@localhost:5432/postgres"
    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            # Fetch all embeddings and texts from the database
            result_set = connection.execute(
                text("""
                SELECT text, embedding
                FROM embeddings
                """)
            ).fetchall()

            # Compute cosine similarity
            max_similarity = float("-inf")
            most_similar_sent = None

            for row in result_set:
                sent, embedding = row
                # print(embedding)
                # print(type(embedding))
                e_list = embedding.strip("{}").split(",")

                # Convert the list of strings to a list of floats
                e_vector = [float(x) for x in e_list]
                # Ensure the embedding is a 1-D NumPy array
                embedding_array = np.array(
                    e_vector, dtype=np.float32
                ).flatten()  # Ensure it's 1-D

                # Compute cosine similarity
                similarity = 1 - cosine(embedded_input, embedding_array)

                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_sent = sent
            # print(type(sent))
            # print(sent)

    except Exception as e:
        print(f"An error occurred during the database operation: {e}")
        return None

    return most_similar_sent if most_similar_sent else None
