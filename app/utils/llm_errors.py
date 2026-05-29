"""Helpers for detecting Gemini / Google API error conditions."""


def is_gemini_quota_exhausted(exc: BaseException) -> bool:
    """
    Return True when Gemini returns 429 / RESOURCE_EXHAUSTED (quota or rate limit).
    Handles LangChain wrappers and google.api_core exceptions.
    """
    seen: set[int] = set()
    current: BaseException | None = exc

    while current is not None and id(current) not in seen:
        seen.add(id(current))

        if type(current).__name__ in ("ResourceExhausted", "TooManyRequests"):
            return True

        text = f"{current} {getattr(current, 'message', '')}".upper()
        if "RESOURCE_EXHAUSTED" in text:
            return True
        if "429" in text and any(
            token in text
            for token in ("QUOTA", "RATE", "LIMIT", "EXHAUSTED", "RESOURCE")
        ):
            return True

        code = getattr(current, "code", None)
        if code is not None and int(code) == 429:
            return True

        status = getattr(current, "status_code", None)
        if status is not None and int(status) == 429:
            return True

        current = current.__cause__ or current.__context__

    return False
