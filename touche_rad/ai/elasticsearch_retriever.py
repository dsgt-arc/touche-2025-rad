from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


class ElasticsearchRetriever:
    def __init__(
        self,
        es_url: str = "https://touche25-rad.webis.de/arguments/",
        index_name: str = "claim_rev",
    ):
        self.es_client = Elasticsearch(es_url, retry_on_timeout=True)
        self.index_name = index_name
        self.embedding_model = SentenceTransformer(
            "NovaSearch/stella_en_400M_v5", trust_remote_code=True
        )

    def get_query_embedding(self, query: str) -> list:
        # get embedding for query using HuggingFace's sentence-transformers
        return self.embedding_model.encode([query])[0]

    def clean_hit(self, hit: dict) -> dict:
        # remove embedding vectors from hit for display purposes
        source = hit["_source"].copy()
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
        return [self.clean_hit(hit) for hit in resp["hits"]["hits"]]
