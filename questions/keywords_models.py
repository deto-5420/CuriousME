from django.db import models

class Keywords(models.Model):
    """
    keywords for questions.
    """

    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = 'Keywords'

    def __str__(self):
        return self.name