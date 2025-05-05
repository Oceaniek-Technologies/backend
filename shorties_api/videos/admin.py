from django.contrib import admin
from .models import Video, VideoHashtag, VideoHashtagRelation, VideoView


class VideoHashtagRelationInline(admin.TabularInline):
    model = VideoHashtagRelation
    extra = 1


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'visibility', 'processing_status', 
                     'view_count', 'created_at']
    list_filter = ['visibility', 'processing_status', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'created_at'
    inlines = [VideoHashtagRelationInline]
    readonly_fields = ['view_count', 'like_count', 'comment_count', 'share_count', 
                      'processing_status', 'duration', 'width', 'height']


@admin.register(VideoHashtag)
class VideoHashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'video_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['video_count']


@admin.register(VideoView)
class VideoViewAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'user', 'ip_address', 'watch_duration', 
                   'watch_percentage', 'created_at']
    list_filter = ['created_at', 'watch_percentage']
    search_fields = ['video__title', 'user__username', 'ip_address']
    date_hierarchy = 'created_at'
