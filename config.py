from os import getenv

config = {
    # Uvicorn settings
    "host": getenv("HOST", "127.0.0.1"),
    "port": int(getenv("PORT", 8000)),
    # Validation settings
    "validate_email": bool(getenv("VALIDATE_EMAIL", True)),
    "email_regex": getenv(
        "EMAIL_REGEX", r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    ),
    "validate_phone": bool(getenv("VALIDATE_PHONE", True)),
    "phone_regex": getenv(
        "PHONE_REGEX", r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"
    ),
    # Graphene settings
    "query_on_mutation": bool(getenv("QUERY_ON_MUTATION", False)),
}
