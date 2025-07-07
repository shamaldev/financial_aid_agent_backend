import json
from json import JSONDecodeError

def _clean_and_parse_json(raw: str) -> dict:
    """
    1) If raw is empty or whitespace: return _fallback_missing_response()
    2) Find the first '{' and the last '}' in raw.
    3) Extract that substring.
    4) Balance braces by appending any missing '}'.
    5) Attempt json.loads on the cleaned snippet.
    6) On failure, return _fallback_malformed().
    """
    if not raw or not raw.strip():
        return _fallback_missing_response()

    # 1) Locate JSON object boundaries
    start = raw.find("{")
    end   = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        print("[JSON PARSE ERROR] No JSON object found in LLM response:\n", raw)
        return _fallback_malformed()

    snippet = raw[start : end + 1].strip()

    # 2) Balance braces if necessary
    open_count  = snippet.count("{")
    close_count = snippet.count("}")
    if close_count < open_count:
        snippet += "}" * (open_count - close_count)

    # 3) Try parsing
    try:
        return json.loads(snippet)
    except JSONDecodeError:
        print("[JSON PARSE ERROR] Malformed JSON after cleaning:\n", snippet)
        return _fallback_malformed()


def _fallback_missing_response() -> dict:
    return {
        "criterion": None,
        "evaluation_guidelines": [],
        "initial_evaluation": {
            "verdict": "Further Review Needed",
            "justification": "LLM returned no content to parse."
        }
    }

def _fallback_malformed() -> dict:
    return {
        "criterion": None,
        "evaluation_guidelines": [],
        "initial_evaluation": {
            "verdict": "Further Review Needed",
            "justification": "Could not parse LLM output—needs human review."
        }
    }
