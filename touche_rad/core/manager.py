from .context import DebateContext
from .machine import DebateMachine
from .strategy import create_strategy

# --- RAG imports ---
from touche_rad.ai.elasticsearch_retriever import ElasticsearchRetriever
from touche_rad.core.rag_pipeline import RAGDebater
from touche_rad.core.strategy.drivers.rag import RAGStrategy


class DebateManager(object):
    def __init__(
        self, client, strategy_name: str = "random", retrieval_mode: str = "text"
    ):
        self.client = client
        self.context = DebateContext(client=client)
        self.machine = DebateMachine(model=self.context)
        self.retrieval_mode = retrieval_mode

        if strategy_name == "rag":
            retriever = ElasticsearchRetriever()
            rag_debater = RAGDebater(retriever, client)
            self.strategy = RAGStrategy(rag_debater, retrieval_mode=retrieval_mode)
        else:
            self.strategy = create_strategy(strategy_name)

    def handle_user_message(self, message: str) -> str:
        """Main entry point for handling a user message."""
        if self.context.is_user_turn():
            self.context.user_input(message)
            if self.context.user_requests_new_topic():
                self.context.start_new_debate()
                return "Okay, let's start a new debate. What's your claim?"
            if self.context.should_conclude():
                self.context.request_conclusion()
                return "I think we've reached a good point to conclude. Do you agree?"
        elif self.context.is_conclusion():
            if message.lower() in ("yes", "y", "ok", "sure"):
                self.context.user_approves_to_conclude()
                return "Great! It was a pleasure debating with you."
            self.context.user_rejects_to_conclude()
        else:
            self.context.start_new_debate()
            return "I'm not sure what to do right now."

        system_response = self.strategy.generate_response(self.context)
        self.context.system_response(system_response)
        return system_response
