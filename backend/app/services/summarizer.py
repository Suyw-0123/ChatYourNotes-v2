"""Summaries extracted text using Gemini API."""

from __future__ import annotations

import os
import unicodedata
from typing import Optional

import google.generativeai as genai

GENERATION_PROMPT = (
    "Summarize the document content into a concise overview and list any key requirements."
)


def configure_client() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable must be set")

    genai.configure(api_key=api_key)


def generate_summary(text: str, model_name: Optional[str] = None) -> str:
    configure_client()

    model = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.GenerativeModel(model)
    prompt = (
        "You are an assistant that writes accurate summaries for aviation regulations. "
        "Summarize the document content into a concise overview and list any key requirements.\n\n"
        f"Document:\n{text}"
    )

    response = client.generate_content(prompt)

    summary = response.text or ""
    summary = unicodedata.normalize("NFKC", summary)
    summary = summary.strip()
    if not summary:
        raise ValueError("Summary generation returned empty text")
    return summary
