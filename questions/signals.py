from django.db.models.signals import post_save
from django.dispatch import receiver
from questions.model import Question

@receiver(post_save, sender=Question)
def update_category_question_count(sender, instance=None, created=False, **kwargs):
    if created:
        category = instance.category
        category.total_questions += 1
        category.save()