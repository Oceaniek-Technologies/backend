from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import os

def video_upload_path(instance, filename):
    """Generate a unique path for uploaded video files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('videos', timezone.now().strftime('%Y/%m/%d'), filename)

def thumbnail_upload_path(instance, filename):
    """Generate a unique path for video thumbnails"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('thumbnails', timezone.now().strftime('%Y/%m/%d'), filename)

class Video(models.Model):
    """
    Model for storing video data
    """
    # Basic video information
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    
    # Video content
    video_file = models.FileField(upload_to=video_upload_path)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_path, blank=True, null=True)
    duration = models.FloatField(default=0)  # in seconds
    
    # Video quality variants
    video_low = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    video_medium = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    video_high = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    
    # Metadata
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    
    # Social engagement metrics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    # Status and visibility
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('unlisted', 'Unlisted')
    ]
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    
    PROCESSING_STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed')
    ]
    processing_status = models.CharField(
        max_length=10, 
        choices=PROCESSING_STATUS_CHOICES,
        default='uploading'
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title or f"Video {self.id}"


class VideoHashtag(models.Model):
    """
    Model for video hashtags
    """
    name = models.CharField(max_length=50, unique=True)
    video_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"#{self.name}"


class VideoHashtagRelation(models.Model):
    """
    Relationship between videos and hashtags
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='hashtag_relations')
    hashtag = models.ForeignKey(VideoHashtag, on_delete=models.CASCADE, related_name='video_relations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('video', 'hashtag')
    
    def __str__(self):
        return f"{self.video} - {self.hashtag}"


class VideoView(models.Model):
    """
    Model to track video views
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='video_views'
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    watch_duration = models.FloatField(default=0)  # in seconds
    watch_percentage = models.FloatField(default=0)  # percentage of video watched
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['video', 'user']),
            models.Index(fields=['video', 'ip_address']),
        ]
    
    def __str__(self):
        return f"View of {self.video} by {self.user or self.ip_address}"
