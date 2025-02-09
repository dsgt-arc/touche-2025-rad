"""Text preprocessing utilities for debate arguments."""

import re
from typing import List, Optional
from transformers import AutoTokenizer


class TextPreprocessor:
    def __init__(self, max_tokens: int = 384):
        """Initialize preprocessor with token limit."""
        self.max_tokens = max_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-mpnet-base-v2"
        )

    def get_token_length(self, text: str) -> int:
        """Get number of tokens in text."""
        return len(self.tokenizer.encode(text))

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        text = " ".join(text.split())
        text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)
        return text.strip()

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using basic punctuation rules."""
        sentences = re.split(r"[.!?]\s+", text)
        return [self.clean_text(sent) for sent in sentences if sent.strip()]

    def find_optimal_chunk_size(self, sentences: List[str]) -> int:
        """Find optimal number of sentences per chunk based on token distribution.

        Args:
            sentences: List of sentences to analyze

        Returns:
            Recommended number of sentences per chunk
        """
        token_lengths = [self.get_token_length(sent) for sent in sentences]
        avg_tokens = sum(token_lengths) / len(token_lengths) if token_lengths else 0

        # Calculate how many average-length sentences would fit within token limit
        # Using 90% of max_tokens to leave some buffer
        safe_token_limit = self.max_tokens * 0.9
        recommended_size = int(safe_token_limit / avg_tokens) if avg_tokens > 0 else 1

        return max(1, min(recommended_size, 10))  # Cap between 1 and 10 sentences

    def chunk_sentences(
        self, sentences: List[str], target_size: Optional[int] = None
    ) -> List[str]:
        """Combine sentences into chunks while respecting token limit.

        Args:
            sentences: List of sentences to chunk
            target_size: Optional target chunk size (if None, will be calculated)

        Returns:
            List of chunked text, each within token limit
        """
        if not sentences:
            return []

        # Determine optimal chunk size if not provided
        if target_size is None:
            target_size = self.find_optimal_chunk_size(sentences)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.get_token_length(sentence)

            # If adding this sentence would exceed limit, save current chunk and start new one
            if current_tokens + sentence_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            # If we've reached target size and next sentence wouldn't exceed token limit,
            # save current chunk and start new one
            elif len(current_chunk) >= target_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            # Add sentence to current chunk
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add any remaining sentences
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def preprocess_with_stats(
        self, text: str, chunk_size: Optional[int] = None
    ) -> tuple[List[str], dict]:
        """Preprocess text and return stats.

        Args:
            text: Text to preprocess
            chunk_size: If provided, combine this many sentences into chunks

        Returns:
            Tuple of (processed_sentences or chunks, stats)
        """
        cleaned_text = self.clean_text(text)
        sentences = self.split_into_sentences(cleaned_text)

        # Collect stats on individual sentences
        token_lengths = [self.get_token_length(sent) for sent in sentences]
        stats = {
            "num_sentences": len(sentences),
            "avg_tokens_per_sentence": sum(token_lengths) / len(sentences)
            if sentences
            else 0,
            "max_tokens": max(token_lengths) if token_lengths else 0,
            "sentences_exceeding_limit": sum(
                1 for x in token_lengths if x > self.max_tokens
            ),
        }

        # Chunk sentences if requested
        if chunk_size:
            chunks = self.chunk_sentences(sentences, chunk_size)
            chunk_tokens = [self.get_token_length(chunk) for chunk in chunks]
            stats.update(
                {
                    "num_chunks": len(chunks),
                    "avg_tokens_per_chunk": sum(chunk_tokens) / len(chunks)
                    if chunks
                    else 0,
                    "max_tokens_in_chunk": max(chunk_tokens) if chunk_tokens else 0,
                }
            )
            return chunks, stats

        return sentences, stats

    def preprocess(self, text: str, chunk_size: Optional[int] = None) -> List[str]:
        """Preprocess text without collecting stats."""
        cleaned_text = self.clean_text(text)
        sentences = self.split_into_sentences(cleaned_text)
        if chunk_size:
            return self.chunk_sentences(sentences, chunk_size)
        return sentences
