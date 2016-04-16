from ipho_core.models import AutoLogin, User

class TokenLoginBackend(object):
    def authenticate(self, token=None):
        if token is None:
            return None
        try:
            user = User.objects.get(autologin__token=token)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
