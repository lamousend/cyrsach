from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    if isinstance(response.data, dict) and "detail" in response.data:
        get_codes = getattr(exc, "get_codes", None)
        codes = get_codes() if callable(get_codes) else None
        if isinstance(codes, str):
            response.data["code"] = codes
    return response