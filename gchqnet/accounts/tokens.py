from django.utils.crypto import get_random_string


def generate_api_token() -> str:
    return get_random_string(32)
