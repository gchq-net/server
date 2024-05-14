from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import User


class UserTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key: str) -> tuple[User, str]:
        try:
            user = User.objects.get(api_token=key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.") from None

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted.")

        return (user, user.api_token)
