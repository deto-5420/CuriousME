from django.apps import AppConfig


class AnswersConfig(AppConfig):
    name = 'answers'
    
    def ready(self):
        import answers.signals