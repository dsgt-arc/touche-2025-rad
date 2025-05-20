from typing import List


class RAGDebater:
    """
    RAG debater with retrieval mode selection: 'text', 'support', or 'attack'.
    """

    def __init__(self, retriever, model_client, top_k: int = 5):
        self.retriever = retriever
        self.model_client = model_client
        self.top_k = top_k

    def generate_response(
        self,
        ctx,
        user_message: str,
        retrieval_mode: str = "text",
        include_evidence: bool = True,
    ) -> str:
        """
        1. Retrieve evidence from retriever using the specified retrieval_mode.
        2. Construct a prompt using user message and evidence.
        3. Generate a response using the model client.
        retrieval_mode: 'text', 'support', or 'attack'
        """
        evidence = self.retriever.retrieve(
            user_message, mode=retrieval_mode, k=self.top_k
        )
        evidence_texts = [item["text"] for item in evidence if "text" in item]
        prompt = self._build_prompt(user_message, evidence_texts, retrieval_mode)
        response = self.model_client.generate(ctx, prompt)
        # TODO: this is gross, just use this interface everywhere it's called
        if include_evidence:
            return response, evidence
        return response

    def _build_prompt(
        self, user_message: str, evidence_texts: List[str], retrieval_mode: str
    ) -> str:
        prompt = (
            f"You are a debate assistant. Use the following {retrieval_mode} evidence to respond to the user's claim.\n"
            f"User claim: {user_message}\n"
        )
        if evidence_texts:
            prompt += "Relevant evidence:\n"
            for idx, text in enumerate(evidence_texts, 1):
                prompt += f"[{idx}] {text}\n"
        prompt += "\nYour response:"
        return prompt
