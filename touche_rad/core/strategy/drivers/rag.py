from touche_rad.core.strategy.drivers.base import BaseStrategy
from touche_rad.core.context import DebateContext
from touche_rad.core.rag_pipeline import RAGDebater


class RAGStrategy(BaseStrategy):
    """
    Strategy that uses the RAGDebater pipeline to generate system responses
    grounded in evidence retrieved from Elasticsearch.
    """

    name = "rag"

    def __init__(self, rag_debater: RAGDebater, retrieval_mode: str = "text"):
        self.rag_debater = rag_debater
        self.retrieval_mode = retrieval_mode

    def get_response_type(self, context: DebateContext):
        # For now, just return None or use context to determine type if needed
        return None

    def generate_response(self, context: DebateContext) -> str:
        user_message = context.last_user_message
        if not user_message:
            return "Please provide a claim to start the debate."
        return self.rag_debater.generate_response(
            user_message, retrieval_mode=self.retrieval_mode
        )
