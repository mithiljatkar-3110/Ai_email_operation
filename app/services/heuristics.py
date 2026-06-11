from __future__ import annotations

from typing import Literal, TypedDict

UrgencyLevel = Literal["Low", "Medium", "High", "Critical"]

SPAM_PHRASES: tuple[str, ...] = (
    "nigerian prince",
    "seo services",
    "earn money fast",
)

SECURITY_PHRASES: tuple[str, ...] = (
    "suspicious login",
    "breach",
    "ransomware",
)

CRITICAL_URGENCY_PHRASES: tuple[str, ...] = (
    "p0",
    "ransomware",
    "cease and desist",
    "breach",
    "suspicious login",
)

HIGH_URGENCY_PHRASES: tuple[str, ...] = (
    "urgent",
    "legal",
)

INTERNAL_DOMAINS: frozenset[str] = frozenset({"internal.com", "mycompany.com"})

PRIORITY_RULES: tuple[tuple[str, int], ...] = (
    ("ransomware", 100),
    ("p0", 80),
    ("legal", 50),
    ("cease and desist", 50),
    ("urgent", 30),
    ("refund", 10),
)

SPAM_PRIORITY_SCORE = 5
SECURITY_PRIORITY_SCORE = 80
DEFAULT_PRIORITY_SCORE = 0


class HeuristicResult(TypedDict):
    is_spam: bool
    is_security: bool
    is_internal: bool
    urgency: UrgencyLevel
    priority_score: int


def _normalize_text(subject: str, body: str) -> str:
    return f"{subject}\n{body}".lower()


def _contains_phrase(text: str, phrase: str) -> bool:
    return phrase in text


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_contains_phrase(text, phrase) for phrase in phrases)


def _sender_domain(sender: str) -> str:
    if "@" not in sender:
        return sender.strip().lower()
    return sender.rsplit("@", 1)[-1].strip().lower()


def _detect_urgency(text: str, *, is_internal: bool) -> UrgencyLevel:
    if _contains_any(text, CRITICAL_URGENCY_PHRASES):
        return "Critical"
    if _contains_any(text, HIGH_URGENCY_PHRASES):
        return "High"
    if is_internal:
        return "Medium"
    return "Low"


def _compute_priority_score(
    text: str,
    *,
    is_spam: bool,
    is_security: bool,
) -> int:
    if is_spam:
        return SPAM_PRIORITY_SCORE

    score = DEFAULT_PRIORITY_SCORE
    for phrase, priority in PRIORITY_RULES:
        if _contains_phrase(text, phrase):
            score = max(score, priority)

    if is_security:
        score = max(score, SECURITY_PRIORITY_SCORE)

    return score


def triage_email(sender: str, subject: str, body: str) -> HeuristicResult:
    """Run synchronous keyword-based triage. No LLM calls."""
    text = _normalize_text(subject, body)
    domain = _sender_domain(sender)

    is_spam = _contains_any(text, SPAM_PHRASES)
    is_security = _contains_any(text, SECURITY_PHRASES)
    is_internal = domain in INTERNAL_DOMAINS

    urgency = _detect_urgency(text, is_internal=is_internal)
    priority_score = _compute_priority_score(
        text,
        is_spam=is_spam,
        is_security=is_security,
    )

    return {
        "is_spam": is_spam,
        "is_security": is_security,
        "is_internal": is_internal,
        "urgency": urgency,
        "priority_score": priority_score,
    }
