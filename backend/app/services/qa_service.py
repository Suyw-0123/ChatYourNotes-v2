"""Question answering over retrieved chunks via Gemini."""

from __future__ import annotations

import os
import unicodedata
from typing import List, Optional

import google.generativeai as genai


def _configure() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable must be set")
    genai.configure(api_key=api_key)
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def answer_question(question: str, contexts: List[str], model_name: Optional[str] = None) -> str:
    if not question.strip():
        raise ValueError("Question must not be empty")
    if not contexts:
        raise ValueError("No context provided for question answering")

    if model_name:
        _configure()
        model = model_name
    else:
        model = _configure()
    client = genai.GenerativeModel(model)

    context_block = "\n\n".join(contexts)
    prompt = (
        "You are an aviation regulatory assistant. Answer the question using only the provided context. "
        "If the answer is not present, respond that you cannot find the answer in the context.\n\n"
        f"Context:\n{context_block}\n\nQuestion: {question}\nAnswer:"
    )

    response = client.generate_content(prompt)

    answer = response.text or ""
    answer = unicodedata.normalize("NFKC", answer)
    answer = answer.strip()
    if not answer:
        raise ValueError("Answer generation returned empty text")
    return answer
