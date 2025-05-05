from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserSettings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'display_name', 'profile_picture', 
            'bio', 'follower_count', 'following_count', 'video_count', 
            'is_verified', 'account_privacy', 'created_at'
        ]
        read_only_fields = ['follower_count', 'following_count', 'video_count', 'is_verified']


class UserPrivateSerializer(UserSerializer):
    """
    Serializer for the user's own profile (includes more fields)
    """
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['notification_enabled', 'email']


class UserPublicSerializer(UserSerializer):
    """
    Serializer for public user profiles (fewer fields)
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'display_name', 'profile_picture', 
            'bio', 'follower_count', 'following_count', 'video_count', 
            'is_verified', 'account_privacy'
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 
            'display_name', 'bio'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'display_name': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            display_name=validated_data.get('display_name', ''),
            bio=validated_data.get('bio', '')
        )
        
        # Create default settings for the user
        UserSettings.objects.create(user=user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = ['display_name', 'bio', 'profile_picture', 'account_privacy', 'notification_enabled']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for user settings
    """
    class Meta:
        model = UserSettings
        fields = [
            'autoplay_videos', 'use_cellular_data', 'video_quality_preference',
            'allow_comments', 'allow_messages', 'notify_on_likes', 
            'notify_on_comments', 'notify_on_follows', 'notify_on_mentions',
            'language'
        ]
