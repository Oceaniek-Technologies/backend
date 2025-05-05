from django.contrib import admin
from .models import Follow, Like, Comment, Share, Notification


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['from_user__username', 'to_user__username']
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'content_type', 'object_id', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'video', 'text_preview', 'parent', 'like_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'text', 'video__title']
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        """Return a preview of the comment text"""
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    
    text_preview.short_description = 'Comment Text'


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'video', 'platform', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['user__username', 'video__title']
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'text_preview', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'text']
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        """Return a preview of the notification text"""
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    
    text_preview.short_description = 'Notification Text'
