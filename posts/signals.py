from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment

@receiver(post_save, sender=Comment)
def handle_new_comment(sender, instance, created, **kwargs):
    if created:
        # Здесь может быть логика отправки уведомлений
        # или автоматической модерации
        pass