from __future__ import annotations

import json
import logging
from typing import Any, TypedDict

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.config import settings
from app.rag.retriever import RetrievedChunk
from app.schemas.classification import ClassificationResult

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2

SYSTEM_INSTRUCTION = (
    "Classify the CURRENT email using prior thread + KB context. "
    "Return JSON only. requires_human=true → escalation_reason required, suggested_reply null. "
    "requires_human=false → suggested_reply required, escalation_reason null."
)


class CurrentEmail(TypedDict):
    sender: str
    subject: str
    body: str


class LLMClassificationError(Exception):
    """Raised when the LLM cannot produce a valid ClassificationResult."""


class LLMClassifier:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if not self.api_key:
            raise LLMClassificationError("GEMINI_API_KEY is not configured")
        if self._client is None:
            logger.info("Initializing Gemini client for model %s", self.model)
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def classify(
        self,
        current_email: CurrentEmail,
        thread_history: str,
        rag_chunks: list[RetrievedChunk],
    ) -> ClassificationResult:
        prompt = self._build_prompt(current_email, thread_history, rag_chunks)
        validation_error: str | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            logger.info("Calling Gemini classification (attempt %s/%s)", attempt, MAX_ATTEMPTS)
            try:
                raw_response = self._call_gemini(prompt, validation_error=validation_error)
                payload = json.loads(raw_response)
                result = ClassificationResult.model_validate(payload)
                logger.info(
                    "Classification succeeded: category=%s sentiment=%s confidence=%.2f",
                    result.category,
                    result.sentiment,
                    result.confidence,
                )
                return result
            except json.JSONDecodeError as exc:
                validation_error = f"Invalid JSON: {exc}"
                logger.warning("Attempt %s failed — %s", attempt, validation_error)
            except ValidationError as exc:
                validation_error = f"Schema validation error: {exc}"
                logger.warning("Attempt %s failed — %s", attempt, validation_error)
            except Exception as exc:
                raise LLMClassificationError(f"Gemini API call failed: {exc}") from exc

        raise LLMClassificationError(
            f"Classification failed after {MAX_ATTEMPTS} attempts. Last error: {validation_error}"
        )

    def _call_gemini(self, prompt: str, validation_error: str | None = None) -> str:
        contents = prompt
        if validation_error:
            contents = (
                f"{prompt}\n\n"
                "Your previous response was invalid.\n"
                f"Error: {validation_error}\n"
                "Return corrected JSON only."
            )

        client = self._get_client()
        response = client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,
                max_output_tokens=settings.classification_max_output_tokens,
                response_mime_type="application/json",
                response_json_schema=_gemini_json_schema(),
            ),
        )

        text = response.text
        if not text or not text.strip():
            raise LLMClassificationError("Gemini returned an empty response")
        return text.strip()

    @staticmethod
    def _build_prompt(
        current_email: CurrentEmail,
        thread_history: str,
        rag_chunks: list[RetrievedChunk],
    ) -> str:
        rag_section = _format_rag_context(rag_chunks)
        return (
            f"KB:\n{rag_section}\n\n"
            f"Prior thread:\n{thread_history.strip()}\n\n"
            "Current email:\n"
            f"From: {current_email['sender']}\n"
            f"Subject: {current_email['subject']}\n"
            f"Body: {current_email['body']}"
        )


def _format_rag_context(rag_chunks: list[RetrievedChunk]) -> str:
    if not rag_chunks:
        return "(none)"

    max_chars = settings.classification_max_rag_chunk_chars
    lines: list[str] = []
    for index, chunk in enumerate(rag_chunks, start=1):
        text = chunk["chunk_text"]
        if len(text) > max_chars:
            text = f"{text[:max_chars].rstrip()}..."
        lines.append(f"[{index}] {chunk['source_doc']}: {text}")
    return "\n".join(lines)


def _gemini_json_schema() -> dict[str, Any]:
    schema = ClassificationResult.model_json_schema()
    return _strip_additional_properties(schema)


def _strip_additional_properties(node: Any) -> Any:
    if isinstance(node, dict):
        cleaned = {
            key: _strip_additional_properties(value)
            for key, value in node.items()
            if key != "additionalProperties"
        }
        return cleaned
    if isinstance(node, list):
        return [_strip_additional_properties(item) for item in node]
    return node


_default_classifier: LLMClassifier | None = None


def get_llm_classifier() -> LLMClassifier:
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = LLMClassifier()
    return _default_classifier


def classify_email(
    current_email: CurrentEmail,
    thread_history: str,
    rag_chunks: list[RetrievedChunk],
) -> ClassificationResult:
    return get_llm_classifier().classify(current_email, thread_history, rag_chunks)
