from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Follow, Like, Comment, Share, Notification
from videos.models import Video

User = get_user_model()

@receiver(post_save, sender=Follow)
def update_follow_counts(sender, instance, created, **kwargs):
    """
    Update follower and following counts when a new follow relationship is created
    """
    if created:
        # Update following count for from_user
        from_user = instance.from_user
        from_user.following_count = Follow.objects.filter(from_user=from_user).count()
        from_user.save(update_fields=['following_count'])
        
        # Update follower count for to_user
        to_user = instance.to_user
        to_user.follower_count = Follow.objects.filter(to_user=to_user).count()
        to_user.save(update_fields=['follower_count'])
        
        # Create a notification for the user being followed
        Notification.objects.create(
            user=to_user,
            from_user=from_user,
            notification_type='follow',
            text=f"{from_user.username} started following you"
        )

@receiver(post_delete, sender=Follow)
def decrease_follow_counts(sender, instance, **kwargs):
    """
    Decrease follower and following counts when a follow relationship is deleted
    """
    # Update following count for from_user
    from_user = instance.from_user
    from_user.following_count = Follow.objects.filter(from_user=from_user).count()
    from_user.save(update_fields=['following_count'])
    
    # Update follower count for to_user
    to_user = instance.to_user
    to_user.follower_count = Follow.objects.filter(to_user=to_user).count()
    to_user.save(update_fields=['follower_count'])

@receiver(post_save, sender=Like)
def update_like_count(sender, instance, created, **kwargs):
    """
    Update the like count on the liked object and create a notification
    """
    if created:
        # For videos
        if instance.content_type == ContentType.objects.get_for_model(Video):
            video = Video.objects.get(id=instance.object_id)
            video.like_count = Like.objects.filter(
                content_type=ContentType.objects.get_for_model(Video),
                object_id=video.id
            ).count()
            video.save(update_fields=['like_count'])
            
            # Create notification for video owner
            if video.user != instance.user:
                Notification.objects.create(
                    user=video.user,
                    from_user=instance.user,
                    notification_type='like',
                    content_type=ContentType.objects.get_for_model(Video),
                    object_id=video.id,
                    text=f"{instance.user.username} liked your video"
                )
        
        # For comments
        elif instance.content_type == ContentType.objects.get_for_model(Comment):
            comment = Comment.objects.get(id=instance.object_id)
            comment.like_count = Like.objects.filter(
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id
            ).count()
            comment.save(update_fields=['like_count'])
            
            # Create notification for comment owner
            if comment.user != instance.user:
                Notification.objects.create(
                    user=comment.user,
                    from_user=instance.user,
                    notification_type='like',
                    content_type=ContentType.objects.get_for_model(Comment),
                    object_id=comment.id,
                    text=f"{instance.user.username} liked your comment"
                )

@receiver(post_delete, sender=Like)
def decrease_like_count(sender, instance, **kwargs):
    """
    Decrease the like count on the liked object when a like is removed
    """
    # For videos
    if instance.content_type == ContentType.objects.get_for_model(Video):
        try:
            video = Video.objects.get(id=instance.object_id)
            video.like_count = Like.objects.filter(
                content_type=ContentType.objects.get_for_model(Video),
                object_id=video.id
            ).count()
            video.save(update_fields=['like_count'])
        except Video.DoesNotExist:
            pass
    
    # For comments
    elif instance.content_type == ContentType.objects.get_for_model(Comment):
        try:
            comment = Comment.objects.get(id=instance.object_id)
            comment.like_count = Like.objects.filter(
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id
            ).count()
            comment.save(update_fields=['like_count'])
        except Comment.DoesNotExist:
            pass

@receiver(post_save, sender=Comment)
def update_comment_count(sender, instance, created, **kwargs):
    """
    Update the comment count on the video and create a notification
    """
    if created:
        video = instance.video
        video.comment_count = Comment.objects.filter(video=video, parent=None).count()
        video.save(update_fields=['comment_count'])
        
        # Create notification for video owner
        if video.user != instance.user:
            Notification.objects.create(
                user=video.user,
                from_user=instance.user,
                notification_type='comment',
                content_type=ContentType.objects.get_for_model(Video),
                object_id=video.id,
                text=f"{instance.user.username} commented on your video"
            )
        
        # If this is a reply, notify the parent comment author
        if instance.parent and instance.parent.user != instance.user:
            Notification.objects.create(
                user=instance.parent.user,
                from_user=instance.user,
                notification_type='comment',
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=instance.parent.id,
                text=f"{instance.user.username} replied to your comment"
            )

@receiver(post_delete, sender=Comment)
def decrease_comment_count(sender, instance, **kwargs):
    """
    Decrease the comment count on the video when a comment is deleted
    """
    try:
        video = instance.video
        video.comment_count = Comment.objects.filter(video=video, parent=None).count()
        video.save(update_fields=['comment_count'])
    except Video.DoesNotExist:
        pass

@receiver(post_save, sender=Share)
def update_share_count(sender, instance, created, **kwargs):
    """
    Update the share count on the video
    """
    if created:
        video = instance.video
        video.share_count = Share.objects.filter(video=video).count()
        video.save(update_fields=['share_count'])
        
        # Create notification for video owner
        if video.user != instance.user:
            Notification.objects.create(
                user=video.user,
                from_user=instance.user,
                notification_type='system',
                content_type=ContentType.objects.get_for_model(Video),
                object_id=video.id,
                text=f"{instance.user.username} shared your video on {instance.platform}"
            )

@receiver(post_delete, sender=Share)
def decrease_share_count(sender, instance, **kwargs):
    """
    Decrease the share count on the video when a share is deleted
    """
    try:
        video = instance.video
        video.share_count = Share.objects.filter(video=video).count()
        video.save(update_fields=['share_count'])
    except Video.DoesNotExist:
        pass