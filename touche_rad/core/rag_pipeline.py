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
            "You are an expert debate partner whose primary goal is to help the user "
            "develop and refine their debating skills. Your role is to thoughtfully challenge "
            "the user's claim by presenting a well-constructed, evidence-based counter-argument.\n\n"
            "Follow these guidelines to ensure your response is of the highest quality:\n\n"
            "1. Direct Engagement: Address the user's claim directly. Identify the core assertion "
            "and respond specifically to its main points, avoiding tangents or unrelated issues.\n\n"
            "2. Logical Reasoning: Construct your counter-argument using clear, logical, and coherent "
            "reasoning. Avoid logical fallacies and ensure each point follows naturally from the evidence "
            "and premises you present.\n\n"
            "3. Evidence-Based: Draw upon the most relevant and compelling evidence available to you "
            "({retrieval_mode}). Integrate facts, examples, or data that strengthen your counter-argument, "
            "but do not include explicit citations or references in your response.\n\n"
            "4. Respectful and Constructive Tone: Maintain a respectful, professional, and encouraging tone "
            "at all times. Your aim is to challenge the user intellectually, not to belittle or dismiss their perspective.\n\n"
            "5. Clarity and Precision: Use clear, concise, and grammatically correct language. Avoid unnecessary "
            "jargon or complexity. Ensure your response is easy to understand and directly addresses the user's claim.\n\n"
            "6. Brevity: Limit your response to 60 words or fewer. Focus on delivering the most impactful and relevant "
            "points within this constraint.\n\n"
            "7. Assertive Utterances: Present your counter-argument as a clear, assertive statement. "
            "Do not use rhetorical questions. Instead, make direct claims or statements that challenge the user's position.\n\n"
            "Your response should embody the highest standards of debate: it should be relevant, well-reasoned, "
            "evidence-based, clear, and respectful. The goal is not simply to disagree, but to help the user sharpen "
            "their arguments and think more critically.\n\n"
            "User claim: {user_message}\n"
        ).format(retrieval_mode=retrieval_mode, user_message=user_message)
        if evidence_texts:
            prompt += "Relevant evidence:\n"
            for idx, text in enumerate(evidence_texts, 1):
                prompt += f"[{idx}] {text}\n"
        prompt += "\nYour response:"
        return prompt
