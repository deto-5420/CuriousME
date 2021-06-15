from django.apps import AppConfig


class RepliesConfig(AppConfig):
    name = 'replies'
    def ready(self):
        import replies.signals