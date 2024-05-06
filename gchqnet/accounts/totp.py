from django.conf import settings
from pyotp import TOTP


class CustomTOTP(TOTP):
    def __init__(self, mac_address: str) -> None:
        secret = mac_address + settings.SECRET_KEY
        super().__init__(secret)

    def byte_secret(self) -> bytes:
        # We don't care if the secret is base32
        # We just want some bytes to feed to the HMAC function
        return self.secret.encode()
