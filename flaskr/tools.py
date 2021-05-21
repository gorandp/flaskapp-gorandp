def char_limit(s: str, n_limit: int, name: str, es_gender: str):
    if len(s) > n_limit:
        # return f"{name} is too large (it has more than {n_limit} characters). "
        return f"{name} es muy larg{es_gender} (tiene más de {n_limit} caracteres). "
    return ""
