from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

import torch


class ElasticsearchRetriever:
    def __init__(
        self,
        es_url: str = "https://touche25-rad.webis.de/arguments/",
        index_name: str = "claimrev",
    ):
        self.es_client = Elasticsearch(
            es_url,
            retry_on_timeout=True,
        )
        self.index_name = index_name

        if torch.cuda.is_available():
            self.embedding_model = SentenceTransformer(
                "dunzhang/stella_en_400M_v5", trust_remote_code=True
            )
        else:
            self.embedding_model = SentenceTransformer(
                "dunzhang/stella_en_400M_v5",
                trust_remote_code=True,
                device="cpu",
                config_kwargs={
                    "use_memory_efficient_attention": False,
                    "unpad_inputs": False,
                },
            )

    def get_query_embedding(self, query: str):
        # get embedding for query using HuggingFace's sentence-transformers
        return self.embedding_model.encode(query, prompt_name="s2p_query")

    def clean_hit(self, hit: dict, rank=1) -> dict:
        # remove embedding vectors from hit for display purposes
        source = hit["_source"].copy()
        source["key"] = rank
        source["id"] = hit["_id"]
        source["score"] = hit["_score"]
        fields_to_remove = [
            "attacks_embedding_stella",
            "supports_embedding_stella",
            "text_embedding_stella",
        ]
        for field in fields_to_remove:
            if field in source:
                del source[field]
        return source

    def retrieve(
        self, query: str, mode: str = "text", k: int = 10, num_candidates: int = 100
    ) -> List[Dict[str, Any]]:
        # retrieve arguments from Elasticsearch using the specified mode
        query_embedding = self.get_query_embedding(query)
        if mode == "text":
            field = "text_embedding_stella"
        elif mode == "support":
            field = "supports_embedding_stella"
        elif mode == "attack":
            field = "attacks_embedding_stella"
        else:
            raise ValueError(f"Unknown retrieval mode: {mode}")

        resp = self.es_client.search(
            index=self.index_name,
            knn={
                "field": field,
                "query_vector": query_embedding,
                "k": k,
                "num_candidates": num_candidates,
            },
        )
        return [
            self.clean_hit(hit, i + 1) for i, hit in enumerate(resp["hits"]["hits"])
        ]
