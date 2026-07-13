"""
Compliance Engine

For each PDPA obligation, this checks every extracted sentence from the
policy against that obligation using TWO signals:

1. Semantic similarity -- does this sentence *mean* roughly the same thing
   as our anchor phrases for this obligation? (handles paraphrasing,
   synonyms, different wording)

2. Keyword verification -- does the sentence contain at least one concrete,
   legally-relevant term for this specific obligation? (guards against
   generic "we care about your privacy" text scoring high on semantic
   similarity without actually addressing the obligation)

A section is only marked "compliant" when BOTH signals agree (two-stage /
AND-logic hybrid) for at least one sentence in the policy. We check every
sentence that clears the semantic bar (not just the single highest-scoring
one) for a keyword match, since the most "on-topic" sentence isn't always
the one that contains the concrete legal term. If no threshold-passing
sentence has a keyword, or nothing clears the threshold at all, it's a "gap".
"""

import numpy as np
from typing import Optional, List, Dict

from .embeddings import embed
from .pdpa_sections import PDPA_SECTIONS

# Tunable thresholds -- raise SEMANTIC_THRESHOLD if you see false positives
# on generic privacy-domain text; lower it if genuine paraphrases are being
# missed.
SEMANTIC_THRESHOLD = 0.55
SEMANTIC_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3


def _keyword_hit(sentence: str, keywords: List[str]) -> Optional[str]:
    lowered = sentence.lower()
    for kw in keywords:
        if kw.lower() in lowered:
            return kw
    return None


def analyze_policy(policy_text_sentences: List[str]) -> List[Dict]:
    """
    Runs the hybrid compliance check for all 8 PDPA sections against the
    given list of extracted sentences. Returns one result dict per section.
    """
    if not policy_text_sentences:
        return [_empty_result(section) for section in PDPA_SECTIONS]

    sentence_embeddings = embed(policy_text_sentences)

    results = []
    for section in PDPA_SECTIONS:
        anchor_embeddings = embed(section["anchor_phrases"])

        # Embeddings are normalised, so a dot product IS the cosine
        # similarity. This matrix gives similarity of every sentence
        # against every anchor phrase for this section in one shot.
        similarity_matrix = np.matmul(sentence_embeddings, anchor_embeddings.T)
        # For each sentence, its best score against any anchor for this section.
        per_sentence_best = similarity_matrix.max(axis=1)

        # Look at every sentence that clears the semantic bar, best first --
        # not just the single highest scoring one. A real policy often has
        # several sentences about the same obligation; the top-scoring one
        # isn't always the one that contains the concrete legal keyword.
        candidate_order = np.argsort(-per_sentence_best)  # descending

        chosen_idx = None
        matched_keyword = None
        for idx in candidate_order:
            idx = int(idx)
            score = float(per_sentence_best[idx])
            if score < SEMANTIC_THRESHOLD:
                break  # sorted descending, so nothing further will pass either
            hit = _keyword_hit(policy_text_sentences[idx], section["keywords"])
            if hit:
                chosen_idx = idx
                matched_keyword = hit
                break

        if chosen_idx is None:
            # No threshold-passing sentence had a keyword match (or none
            # passed the threshold at all) -- fall back to the single best
            # scoring sentence purely for display purposes.
            chosen_idx = int(candidate_order[0])

        best_semantic_score = float(per_sentence_best[chosen_idx])
        best_sentence = policy_text_sentences[chosen_idx]
        keyword_score = 1.0 if matched_keyword else 0.0

        final_score = (
            SEMANTIC_WEIGHT * best_semantic_score + KEYWORD_WEIGHT * keyword_score
        )

        semantic_pass = best_semantic_score >= SEMANTIC_THRESHOLD
        if semantic_pass and matched_keyword:
            status = "compliant"
            explanation = (
                f'This clause semantically matches "{section["title"]}" '
                f'and contains the concrete term "{matched_keyword}", '
                f"so it is flagged as compliant."
            )
        elif semantic_pass and not matched_keyword:
            status = "gap"
            explanation = (
                f'This clause sounds related to "{section["title"]}" '
                f"but no clause found contains a specific keyword tied to "
                f"this obligation, so it is treated as generic privacy "
                f'language rather than a real compliance commitment under '
                f'{section["section_number"]}.'
            )
        else:
            status = "gap"
            explanation = (
                f'No clause in the policy sufficiently addresses "{section["title"]}". '
                f"Possible compliance gap under {section['section_number']}."
            )

        results.append(
            {
                "id": section["id"],
                "section_number": section["section_number"],
                "title": section["title"],
                "description": section["description"],
                "status": status,
                "final_score": round(final_score, 3),
                "best_match": {
                    "text": best_sentence,
                    "semantic_score": round(best_semantic_score, 3),
                    "keyword_hit": bool(matched_keyword),
                    "matched_keyword": matched_keyword,
                },
                "explanation": explanation,
            }
        )

    return results


def _empty_result(section: dict) -> dict:
    return {
        "id": section["id"],
        "section_number": section["section_number"],
        "title": section["title"],
        "description": section["description"],
        "status": "gap",
        "final_score": 0.0,
        "best_match": None,
        "explanation": "No usable text was extracted from the supplied policy.",
    }