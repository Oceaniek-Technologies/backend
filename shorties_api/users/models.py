from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User Model for Shorties app
    Extends Django's AbstractUser to add app-specific fields
    """
    # Display name (different from username)
    display_name = models.CharField(_("display name"), max_length=50, blank=True)
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Bio/description
    bio = models.TextField(_("biography"), max_length=500, blank=True)
    
    # User statistics
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    video_count = models.PositiveIntegerField(default=0)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    
    # Settings and preferences
    notification_enabled = models.BooleanField(default=True)
    account_privacy = models.CharField(
        max_length=10,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )
    
    # Additional timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ['-date_joined']


class UserSettings(models.Model):
    """
    User Settings Model
    Stores user preferences and application settings
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='settings'
    )
    
    # Video autoplay settings
    autoplay_videos = models.BooleanField(default=True)
    
    # Data usage preferences
    use_cellular_data = models.BooleanField(default=True)
    video_quality_preference = models.CharField(
        max_length=10,
        choices=[
            ('auto', 'Auto'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='auto'
    )
    
    # Privacy settings
    allow_comments = models.BooleanField(default=True)
    allow_messages = models.BooleanField(default=True)
    
    # Notification preferences
    notify_on_likes = models.BooleanField(default=True)
    notify_on_comments = models.BooleanField(default=True)
    notify_on_follows = models.BooleanField(default=True)
    notify_on_mentions = models.BooleanField(default=True)
    
    # Language preference
    language = models.CharField(max_length=10, default='en')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s settings"
