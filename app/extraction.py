"""
Extraction Module

Job: take the raw text of a privacy policy and break it into clean,
individual sentences/clauses that we can then check against each PDPA
obligation. Kept deliberately simple (regex-based) rather than depending
on a heavy NLP toolkit -- easy to explain in a viva, and good enough for
well-formed policy text.
"""

import re


MIN_SENTENCE_LENGTH = 15  # characters -- filters out stray fragments/bullets


def extract_sentences(policy_text: str) -> list[str]:
    """
    Splits policy text into a list of cleaned sentences.

    Steps:
    1. Normalise whitespace/newlines so bullet points and line breaks
       don't get glued to neighbouring sentences.
    2. Split on sentence-ending punctuation (. ! ?) followed by a space
       or line break.
    3. Strip bullet characters and extra whitespace.
    4. Drop anything too short to be a meaningful clause.
    """
    if not policy_text or not policy_text.strip():
        return []

    # Treat bullet points / line breaks as sentence boundaries too, so a
    # bullet list doesn't get merged into one giant "sentence".
    normalised = re.sub(r"[•●▪\-\*]\s*", "\n", policy_text)
    normalised = re.sub(r"\s*\n\s*", "\n", normalised)

    # Split into rough sentences on '.', '!', '?' followed by whitespace,
    # as well as on newlines.
    raw_pieces = re.split(r"(?<=[.!?])\s+|\n", normalised)

    sentences = []
    for piece in raw_pieces:
        cleaned = piece.strip(" \t\r\n-•●▪*")
        if len(cleaned) >= MIN_SENTENCE_LENGTH:
            sentences.append(cleaned)

    return sentences
