from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from videos.models import Video
from users.serializers import UserPublicSerializer
from .models import Follow, Like, Comment, Share, Notification

User = get_user_model()

class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for follow relationships
    """
    from_user = UserPublicSerializer(read_only=True)
    to_user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'from_user', 'to_user', 'created_at']
        read_only_fields = ['from_user', 'created_at']


class FollowCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating follow relationships
    """
    to_user_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = Follow
        fields = ['to_user_id']
    
    def validate_to_user_id(self, value):
        """
        Validate that the user to follow exists and is not the current user
        """
        request = self.context.get('request')
        if request.user.id == value:
            raise serializers.ValidationError("You cannot follow yourself.")
            
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User to follow does not exist.")
            
        return value
    
    def create(self, validated_data):
        """
        Create a follow relationship
        """
        to_user_id = validated_data.pop('to_user_id')
        from_user = self.context['request'].user
        to_user = User.objects.get(pk=to_user_id)
        
        # Create the follow relationship
        follow = Follow.objects.create(from_user=from_user, to_user=to_user)
        
        # Update user counts
        from_user.following_count = Follow.objects.filter(from_user=from_user).count()
        from_user.save(update_fields=['following_count'])
        
        to_user.follower_count = Follow.objects.filter(to_user=to_user).count()
        to_user.save(update_fields=['follower_count'])
        
        return follow


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for likes
    """
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['user', 'created_at']


class LikeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating likes
    """
    object_type = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = Like
        fields = ['object_type', 'object_id']
    
    def validate(self, attrs):
        """
        Validate that the object to like exists
        """
        object_type = attrs.pop('object_type')
        object_id = attrs['object_id']
        
        # Map object_type to ContentType
        content_types = {
            'video': Video,
            'comment': Comment
        }
        
        if object_type not in content_types:
            raise serializers.ValidationError({
                'object_type': f"Invalid object type. Must be one of: {', '.join(content_types.keys())}"
            })
        
        model_class = content_types[object_type]
        content_type = ContentType.objects.get_for_model(model_class)
        
        # Check if object exists
        try:
            content_object = model_class.objects.get(pk=object_id)
        except model_class.DoesNotExist:
            raise serializers.ValidationError({
                'object_id': f"{object_type.capitalize()} with id {object_id} does not exist."
            })
        
        # Add content_type to validated data
        attrs['content_type'] = content_type
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a like or unlike if it already exists
        """
        user = self.context['request'].user
        content_type = validated_data['content_type']
        object_id = validated_data['object_id']
        
        # Check if like already exists
        like, created = Like.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id
        )
        
        if not created:
            # User already liked, so unlike
            like.delete()
            
            # Update like count on the content object
            content_object = content_type.get_object_for_this_type(pk=object_id)
            content_object.like_count = Like.objects.filter(
                content_type=content_type,
                object_id=object_id
            ).count()
            content_object.save(update_fields=['like_count'])
            
            # Return None to indicate the like was removed
            return None
        
        # Update like count on the content object
        content_object = content_type.get_object_for_this_type(pk=object_id)
        content_object.like_count = Like.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).count()
        content_object.save(update_fields=['like_count'])
        
        return like


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments
    """
    user = UserPublicSerializer(read_only=True)
    reply_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'video', 'user', 'text', 'parent', 
            'like_count', 'reply_count', 'liked_by_me',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'like_count', 'created_at', 'updated_at']
    
    def get_reply_count(self, obj):
        """
        Get the number of replies to this comment
        """
        return obj.replies.count()
    
    def get_liked_by_me(self, obj):
        """
        Check if the current user has liked this comment
        """
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
            
        return Like.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=obj.id
        ).exists()


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments
    """
    class Meta:
        model = Comment
        fields = ['video', 'text', 'parent']
    
    def validate_parent(self, value):
        """
        Validate that parent comment exists and belongs to the same video
        """
        if value is not None:
            video_id = self.initial_data.get('video')
            if str(value.video.id) != str(video_id):
                raise serializers.ValidationError(
                    "Parent comment does not belong to the specified video."
                )
        return value
    
    def create(self, validated_data):
        """
        Create a comment and update video comment count
        """
        user = self.context['request'].user
        comment = Comment.objects.create(user=user, **validated_data)
        
        # Update video comment count
        video = validated_data['video']
        video.comment_count = Comment.objects.filter(video=video, parent=None).count()
        video.save(update_fields=['comment_count'])
        
        return comment


class ShareSerializer(serializers.ModelSerializer):
    """
    Serializer for video shares
    """
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Share
        fields = ['id', 'video', 'user', 'platform', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        """
        Record a share and update video share count
        """
        user = self.context['request'].user
        share = Share.objects.create(user=user, **validated_data)
        
        # Update video share count
        video = validated_data['video']
        video.share_count = Share.objects.filter(video=video).count()
        video.save(update_fields=['share_count'])
        
        return share


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications
    """
    from_user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'text', 'from_user', 
            'content_type', 'object_id', 'is_read', 'created_at'
        ]
        read_only_fields = fields
