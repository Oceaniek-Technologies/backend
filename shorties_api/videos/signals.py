from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Video, VideoHashtag, VideoHashtagRelation

User = get_user_model()

@receiver(post_save, sender=Video)
def update_user_video_count(sender, instance, created, **kwargs):
    """
    Update user's video count when a new video is created
    """
    if created:
        user = instance.user
        user.video_count = Video.objects.filter(user=user).count()
        user.save(update_fields=['video_count'])

@receiver(post_delete, sender=Video)
def decrease_user_video_count(sender, instance, **kwargs):
    """
    Decrease user's video count when a video is deleted
    """
    user = instance.user
    user.video_count = Video.objects.filter(user=user).count()
    user.save(update_fields=['video_count'])

@receiver(post_save, sender=VideoHashtagRelation)
def update_hashtag_count(sender, instance, created, **kwargs):
    """
    Update hashtag video count when a new relation is created
    """
    if created:
        hashtag = instance.hashtag
        hashtag.video_count = VideoHashtagRelation.objects.filter(hashtag=hashtag).count()
        hashtag.save(update_fields=['video_count'])

@receiver(post_delete, sender=VideoHashtagRelation)
def decrease_hashtag_count(sender, instance, **kwargs):
    """
    Decrease hashtag video count when a relation is deleted
    """
    hashtag = instance.hashtag
    hashtag.video_count = VideoHashtagRelation.objects.filter(hashtag=hashtag).count()
    hashtag.save(update_fields=['video_count'])