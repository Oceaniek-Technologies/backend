from rest_framework import serializers
from django.conf import settings
from .models import Video, VideoHashtag, VideoHashtagRelation, VideoView
from users.serializers import UserPublicSerializer
import re

class VideoHashtagSerializer(serializers.ModelSerializer):
    """
    Serializer for video hashtags
    """
    class Meta:
        model = VideoHashtag
        fields = ['id', 'name', 'video_count']
        read_only_fields = ['video_count']


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for videos
    """
    user = UserPublicSerializer(read_only=True)
    hashtags = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'user', 'video_file', 
            'thumbnail', 'duration', 'width', 'height',
            'view_count', 'like_count', 'comment_count', 'share_count',
            'visibility', 'processing_status', 'created_at', 'hashtags',
            'video_low', 'video_medium', 'video_high'
        ]
        read_only_fields = [
            'duration', 'width', 'height', 'view_count', 'like_count',
            'comment_count', 'share_count', 'processing_status',
            'video_low', 'video_medium', 'video_high'
        ]
    
    def get_hashtags(self, obj):
        """
        Get all hashtags associated with this video
        """
        hashtag_relations = VideoHashtagRelation.objects.filter(video=obj)
        hashtags = [relation.hashtag for relation in hashtag_relations]
        return VideoHashtagSerializer(hashtags, many=True).data
    
    def validate_video_file(self, value):
        """
        Validate the video file size
        """
        if value.size > settings.MAX_VIDEO_SIZE:
            raise serializers.ValidationError(
                f"Video file is too large. Maximum size is {settings.MAX_VIDEO_SIZE / (1024 * 1024)}MB"
            )
        return value


class VideoCreateSerializer(VideoSerializer):
    """
    Serializer for creating videos
    """
    hashtag_text = serializers.CharField(required=False, write_only=True)
    
    class Meta(VideoSerializer.Meta):
        fields = VideoSerializer.Meta.fields + ['hashtag_text']
    
    def create(self, validated_data):
        """
        Create a video and extract hashtags from the description
        """
        hashtag_text = validated_data.pop('hashtag_text', '')
        
        # Create the video
        video = Video.objects.create(**validated_data)
        
        # Extract and save hashtags
        if hashtag_text:
            self._process_hashtags(video, hashtag_text)
        
        return video
    
    def _process_hashtags(self, video, hashtag_text):
        """
        Process hashtags and create relationships
        """
        # Extract hashtags using regex
        hashtags = re.findall(r'#(\w+)', hashtag_text)
        
        # Create or update hashtags and relationships
        for tag_name in hashtags:
            tag_name = tag_name.lower()
            if len(tag_name) > 50:
                continue  # Skip if hashtag is too long
                
            # Get or create the hashtag
            hashtag, created = VideoHashtag.objects.get_or_create(name=tag_name)
            
            # Create relationship between video and hashtag
            VideoHashtagRelation.objects.create(video=video, hashtag=hashtag)
            
            # Update hashtag count
            hashtag.video_count = VideoHashtagRelation.objects.filter(hashtag=hashtag).count()
            hashtag.save()


class VideoUpdateSerializer(VideoSerializer):
    """
    Serializer for updating videos
    """
    hashtag_text = serializers.CharField(required=False, write_only=True)
    
    class Meta(VideoSerializer.Meta):
        fields = ['title', 'description', 'visibility', 'thumbnail', 'hashtag_text']
    
    def update(self, instance, validated_data):
        """
        Update a video and its hashtags
        """
        hashtag_text = validated_data.pop('hashtag_text', None)
        
        # Update the video instance
        instance = super().update(instance, validated_data)
        
        # Update hashtags if provided
        if hashtag_text is not None:
            # Delete existing hashtag relations
            VideoHashtagRelation.objects.filter(video=instance).delete()
            
            # Process new hashtags
            hashtags = re.findall(r'#(\w+)', hashtag_text)
            for tag_name in hashtags:
                tag_name = tag_name.lower()
                if len(tag_name) > 50:
                    continue
                
                hashtag, created = VideoHashtag.objects.get_or_create(name=tag_name)
                VideoHashtagRelation.objects.create(video=instance, hashtag=hashtag)
                
                # Update hashtag count
                hashtag.video_count = VideoHashtagRelation.objects.filter(hashtag=hashtag).count()
                hashtag.save()
                
        return instance


class VideoViewSerializer(serializers.ModelSerializer):
    """
    Serializer for video views
    """
    class Meta:
        model = VideoView
        fields = ['id', 'video', 'watch_duration', 'watch_percentage', 'created_at']
        read_only_fields = ['id', 'created_at']
        
    def create(self, validated_data):
        """
        Create or update a video view
        """
        # Set user from request if authenticated
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['user'] = user
        else:
            # Get client IP address if user is not authenticated
            validated_data['ip_address'] = self._get_client_ip(self.context['request'])
        
        # Create the view record
        view = VideoView.objects.create(**validated_data)
        
        # Update video view count
        video = validated_data['video']
        video.view_count = VideoView.objects.filter(video=video).count()
        video.save()
        
        return view
    
    def _get_client_ip(self, request):
        """
        Get the client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
