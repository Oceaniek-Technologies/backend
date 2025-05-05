from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserSettings

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """
    Create UserSettings when a new User is created
    """
    if created:
        UserSettings.objects.get_or_create(user=instance)