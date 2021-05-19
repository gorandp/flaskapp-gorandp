def char_limit(s: str, n_limit: int, name: str):
    if len(s) > n_limit:
        return f"{name} is too large (it has more than {n_limit} characters). "
    return ""
