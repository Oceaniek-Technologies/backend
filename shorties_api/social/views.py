from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Follow, Like, Comment, Share, Notification
from .serializers import (
    FollowSerializer, FollowCreateSerializer,
    LikeSerializer, LikeCreateSerializer,
    CommentSerializer, CommentCreateSerializer,
    ShareSerializer, NotificationSerializer
)
from videos.models import Video

User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    """
    API endpoint for follow relationships
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only follow relationships relevant to the current user
        """
        user = self.request.user
        return Follow.objects.filter(Q(from_user=user) | Q(to_user=user))
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return FollowCreateSerializer
        return FollowSerializer
    
    def perform_create(self, serializer):
        """
        Create a follow relationship
        """
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggle following/unfollowing a user
        """
        serializer = FollowCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            from_user = request.user
            to_user_id = serializer.validated_data['to_user_id']
            to_user = User.objects.get(pk=to_user_id)
            
            # Check if already following
            try:
                follow = Follow.objects.get(from_user=from_user, to_user=to_user)
                # Unfollow
                follow.delete()
                
                # Update counts
                from_user.following_count = Follow.objects.filter(from_user=from_user).count()
                from_user.save(update_fields=['following_count'])
                
                to_user.follower_count = Follow.objects.filter(to_user=to_user).count()
                to_user.save(update_fields=['follower_count'])
                
                return Response({"status": "unfollowed"}, status=status.HTTP_200_OK)
            except Follow.DoesNotExist:
                # Follow
                follow = Follow.objects.create(from_user=from_user, to_user=to_user)
                
                # Update counts
                from_user.following_count = Follow.objects.filter(from_user=from_user).count()
                from_user.save(update_fields=['following_count'])
                
                to_user.follower_count = Follow.objects.filter(to_user=to_user).count()
                to_user.save(update_fields=['follower_count'])
                
                return Response({"status": "followed"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def followers(self, request):
        """
        Return users who follow the authenticated user
        """
        user = request.user
        follows = Follow.objects.filter(to_user=user)
        followers = [follow.from_user for follow in follows]
        
        from users.serializers import UserPublicSerializer
        serializer = UserPublicSerializer(followers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def following(self, request):
        """
        Return users that the authenticated user follows
        """
        user = request.user
        follows = Follow.objects.filter(from_user=user)
        following = [follow.to_user for follow in follows]
        
        from users.serializers import UserPublicSerializer
        serializer = UserPublicSerializer(following, many=True)
        return Response(serializer.data)


class LikeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for likes
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only likes from the current user
        """
        return Like.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return LikeCreateSerializer
        return LikeSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Toggle like/unlike
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        
        if instance is None:
            # Item was unliked
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)
        
        # Item was liked
        return Response({"status": "liked"}, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        """
        Create a like or unlike if it already exists
        """
        return serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Return comments based on query parameters
        """
        queryset = Comment.objects.all()
        
        # Filter by video if specified
        video_id = self.request.query_params.get('video', None)
        if video_id:
            queryset = queryset.filter(video_id=video_id)
            
        # Filter by parent comment if specified
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            if parent_id == '0':
                # Get top-level comments (no parent)
                queryset = queryset.filter(parent=None)
            else:
                # Get replies to a specific comment
                queryset = queryset.filter(parent_id=parent_id)
        else:
            # Default to top-level comments only
            queryset = queryset.filter(parent=None)
            
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """
        Create a comment with the authenticated user
        """
        serializer.save(user=self.request.user)


class ShareViewSet(viewsets.ModelViewSet):
    """
    API endpoint for video shares
    """
    serializer_class = ShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only shares from the current user
        """
        return Share.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a share with the authenticated user
        """
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only notifications for the current user
        """
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark notifications as read
        """
        notification_ids = request.data.get('ids', [])
        if notification_ids:
            # Mark specific notifications as read
            Notification.objects.filter(
                user=request.user,
                id__in=notification_ids
            ).update(is_read=True)
        else:
            # Mark all notifications as read
            Notification.objects.filter(user=request.user).update(is_read=True)
            
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Return the count of unread notifications
        """
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"count": count})
