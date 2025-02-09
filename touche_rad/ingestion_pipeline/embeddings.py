"""Embedding generation for debate arguments."""

import torch
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from tqdm import tqdm


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
