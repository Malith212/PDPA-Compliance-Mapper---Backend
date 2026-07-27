
import numpy as np
from typing import Optional, List, Dict

from .embeddings import embed
from .pdpa_sections import PDPA_SECTIONS

#Step 5: Walk down the list, checking the threshold AND the keyword
SEMANTIC_THRESHOLD = 0.55
SEMANTIC_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3

# Checks if a sentence contains any one of a list of keywords, and tells you which one it found.
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

    #Convert policy_text_sentences into "meaning numbers"
    sentence_embeddings = embed(policy_text_sentences)

    results = []
    for section in PDPA_SECTIONS:
        #Convert anchor_embeddings into "meaning numbers"
        anchor_embeddings = embed(section["anchor_phrases"])

        # Step 2: Compare EVERY sentence against EVERY anchor phrase
        similarity_matrix = np.matmul(sentence_embeddings, anchor_embeddings.T)

        # Step 3: For each sentence, keep only its BEST score
        per_sentence_best = similarity_matrix.max(axis=1)


        #Step 4: Sort sentences by score, highest first
        candidate_order = np.argsort(-per_sentence_best)  # descending

        # No winner found yet -- start empty
        chosen_idx = None
        matched_keyword = None

        # Go through sentences, BEST score first (most relevant first)
        for idx in candidate_order:
            idx = int(idx)
            score = float(per_sentence_best[idx])

            # Scores are sorted highest to lowest, so once we hit one below the
            # threshold, every sentence after it will also fail -- stop checking.
            if score < SEMANTIC_THRESHOLD:
                break  # sorted descending, so nothing further will pass either

            # This sentence is relevant enough -- now check if it ALSO has a
            # real legal keyword (not just similar-sounding text)
            hit = _keyword_hit(policy_text_sentences[idx], section["keywords"])
            if hit:
        # Found a sentence that passes BOTH checks -- this is our winner.
        # Save it and stop looking at any more sentences.
                chosen_idx = idx
                matched_keyword = hit
                break

        if chosen_idx is None:
            # just pick the top-scoring one anyway
            chosen_idx = int(candidate_order[0])

        # Look up the winning sentence's actual score and text using its index
        best_semantic_score = float(per_sentence_best[chosen_idx])
        best_sentence = policy_text_sentences[chosen_idx]

        # Did we find a keyword? Full score (1.0) if yes, zero if no
        keyword_score = 1.0 if matched_keyword else 0.0

        final_score = (
            SEMANTIC_WEIGHT * best_semantic_score + KEYWORD_WEIGHT * keyword_score
        )

        semantic_pass = best_semantic_score >= SEMANTIC_THRESHOLD
        if semantic_pass and matched_keyword:
            status = "compliant"
            explanation = (
                f'This clause semantically matches "{section["title"]}", '
                f"so it is flagged as compliant."
            )
        elif semantic_pass and not matched_keyword:
            status = "gap"
            explanation = (
                f'No clause in the policy sufficiently addresses "{section["title"]}". '
                f"Possible compliance gap under {section['section_number']}."
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