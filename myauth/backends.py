from django.contrib.auth import get_user_model
User = get_user_model()

class SettingsBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            user = User(username=username, password=username)
            user.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


