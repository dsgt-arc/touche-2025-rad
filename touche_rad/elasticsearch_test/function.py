from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# Initialize Elasticsearch client and embedding model
elasticsearch_url = "https://touche25-rad.webis.de/arguments/"
es_client = Elasticsearch(elasticsearch_url, retry_on_timeout=True)
index_name = "claim_rev"
embedding_model = SentenceTransformer(
    "dunzhang/stella_en_400M_v5", trust_remote_code=True
)


def get_query_embedding(query: str) -> list:
    """Generate embedding for the given query using Stella model."""
    return embedding_model.encode(query, prompt_name="s2p_query")


def clean_hit(hit: dict) -> dict:
    """Remove embedding vectors from hit for display purposes."""
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


def search_by_text(query: str, k: int = 10, num_candidates: int = 100) -> list:
    """Search for arguments based on text similarity."""
    query_embedding = get_query_embedding(query)
    resp = es_client.search(
        index=index_name,
        knn={
            "field": "text_embedding_stella",
            "query_vector": query_embedding,
            "k": k,
            "num_candidates": num_candidates,
        },
    )
    return [clean_hit(hit) for hit in resp["hits"]["hits"]]


def search_by_support(query: str, k: int = 10, num_candidates: int = 100) -> list:
    """Search for arguments that support the query."""
    query_embedding = get_query_embedding(query)
    resp = es_client.search(
        index=index_name,
        knn={
            "field": "supports_embedding_stella",
            "query_vector": query_embedding,
            "k": k,
            "num_candidates": num_candidates,
        },
    )
    return [clean_hit(hit) for hit in resp["hits"]["hits"]]


def search_by_attack(query: str, k: int = 10, num_candidates: int = 100) -> list:
    """Search for arguments that attack the query."""
    query_embedding = get_query_embedding(query)
    resp = es_client.search(
        index=index_name,
        knn={
            "field": "attacks_embedding_stella",
            "query_vector": query_embedding,
            "k": k,
            "num_candidates": num_candidates,
        },
    )
    return [clean_hit(hit) for hit in resp["hits"]["hits"]]


def search_all(query: str, k: int = 10, num_candidates: int = 100) -> dict:
    """Search for arguments using all three methods and return combined results."""
    return {
        "text_similarity": search_by_text(query, k, num_candidates),
        "supporting": search_by_support(query, k, num_candidates),
        "attacking": search_by_attack(query, k, num_candidates),
    }
