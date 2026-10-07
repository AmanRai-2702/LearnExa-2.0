def is_invalid_key_error(error: Exception | None) -> bool:
    """True if a Gemini error means "your API key is not accepted".

    Gemini reports a wrong key in two ways: HTTP 401/403, or HTTP 400 with a
    message such as "API key not valid". A 400 about something else (for
    example a malformed request) is NOT a key problem.
    """
    code = getattr(error, "code", None)
    if code in (401, 403):
        return True
    return code == 400 and "api key" in str(error).lower()