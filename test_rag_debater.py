from touche_rad.ai.elasticsearch_retriever import ElasticsearchRetriever
from touche_rad.core.rag_pipeline import RAGDebater
from touche_rad.core.strategy.drivers.rag import RAGStrategy
from touche_rad.ai.tensorzero import TensorZeroClient
from touche_rad.core.context import DebateContext
from touche_rad.core.machine import DebateMachine

from dotenv import load_dotenv


load_dotenv()


def main():
    retriever = ElasticsearchRetriever()
    model_client = TensorZeroClient()
    rag_debater = RAGDebater(retriever, model_client)
    strategy = RAGStrategy(rag_debater, retrieval_mode="text")

    context = DebateContext(client=model_client)
    _ = DebateMachine(model=context)

    user_claim = "Social media has a negative impact on mental health."
    context.user_input(user_claim)

    # Generate response
    response = strategy.generate_response(context)
    print("User claim:", user_claim)
    print("Debater response:", response)


if __name__ == "__main__":
    main()
