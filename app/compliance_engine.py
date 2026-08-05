import numpy as np
from typing import Optional, List, Dict, Tuple

from .embeddings import embed
from .pdpa_sections import PDPA_SECTIONS

#Step 5: Walk down the list, checking the threshold AND the keyword
SEMANTIC_THRESHOLD = 0.55
SEMANTIC_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3

# How many characters to look back from a keyword match when checking for
# negation. Wide enough to catch "You cannot request deletion of your data"
# (cue is several words before the keyword phrase), narrow enough to avoid
# picking up negation cues from an unrelated earlier clause in the same
# sentence.
NEGATION_WINDOW_CHARS = 40

# Words/phrases that flip a keyword match from "right granted" to
# "right denied". Kept deliberately simple (substring match, same style as
# _keyword_hit) rather than full NLP negation detection -- good enough for
# well-formed policy clauses, easy to explain and extend.
NEGATION_CUES = [
    "cannot", "can not", "can't", "will not", "won't", "does not", "doesn't",
    "do not", "don't", "unable to", "not able to", "not permitted",
    "not allowed", "not possible", "not entitled", "no longer able",
    "not eligible", "shall not", "may not", "never", "not be able",
    "without the ability", "no right to",
]


# Checks if a sentence contains any one of a list of keywords, and tells you
# which one it found -- and whether that match is negated (i.e. the sentence
# is DENYING the right rather than granting it).
def _keyword_hit(sentence: str, keywords: List[str]) -> Tuple[Optional[str], bool]:
    """
    Returns (matched_keyword, is_negated).
    matched_keyword is None if no keyword is found at all.
    is_negated is only meaningful when matched_keyword is not None.
    """
    lowered = sentence.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        idx = lowered.find(kw_lower)
        if idx == -1:
            continue

        window_start = max(0, idx - NEGATION_WINDOW_CHARS)
        preceding_window = lowered[window_start:idx]
        is_negated = any(cue in preceding_window for cue in NEGATION_CUES)

        return kw, is_negated

    return None, False


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

        # Track the best-scoring sentence that matched a keyword but was
        # NEGATED, in case we never find a genuine (non-negated) match.
        negated_idx = None
        negated_keyword = None

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
            hit, is_negated = _keyword_hit(policy_text_sentences[idx], section["keywords"])

            if hit and not is_negated:
                # Found a sentence that passes BOTH checks and isn't denying
                # the right -- this is our winner. Stop looking.
                chosen_idx = idx
                matched_keyword = hit
                break

            if hit and is_negated and negated_idx is None:
                # Remember the highest-scoring NEGATED hit as a fallback --
                # but keep searching lower-ranked sentences for a genuine,
                # non-negated match first.
                negated_idx = idx
                negated_keyword = hit

        is_violation = False
        if chosen_idx is None:
            if negated_idx is not None:
                # No genuine match anywhere in the policy, but we did find a
                # sentence that explicitly denies this right.
                chosen_idx = negated_idx
                matched_keyword = None  # doesn't count toward keyword_score
                is_violation = True
            else:
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

        if is_violation:
            status = "violation"
            explanation = (
                f'This clause appears to explicitly deny "{section["title"]}", '
                f"which conflicts with {section['section_number']}."
            )
        elif semantic_pass and matched_keyword:
            status = "compliant"
            explanation = (
                f'This clause semantically matches "{section["title"]}", '
                f"so it is flagged as compliant."
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
                    "matched_keyword": matched_keyword if matched_keyword else negated_keyword,
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