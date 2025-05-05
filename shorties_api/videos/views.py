from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import F, Count
from django.conf import settings
import uuid

from .models import Video, VideoHashtag, VideoView
from .serializers import (
    VideoSerializer, VideoCreateSerializer, VideoUpdateSerializer,
    VideoHashtagSerializer, VideoViewSerializer
)
from .utils import process_video
from social.models import Like


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner of the video
        return obj.user == request.user


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for videos
    """
    queryset = Video.objects.filter(processing_status='ready', visibility='public')
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'view_count', 'like_count']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        """
        Return videos based on filters and user permission
        """
        user = self.request.user
        
        # Base queryset
        queryset = Video.objects.all()
        
        # Apply visibility filters
        if user.is_authenticated:
            # Authenticated users can see public videos and their own videos
            queryset = queryset.filter(
                (models.Q(visibility='public') & models.Q(processing_status='ready')) |
                models.Q(user=user)
            )
        else:
            # Anonymous users can only see public videos
            queryset = queryset.filter(visibility='public', processing_status='ready')
        
        # Apply additional filters from query parameters
        hashtag = self.request.query_params.get('hashtag', None)
        if hashtag:
            queryset = queryset.filter(hashtag_relations__hashtag__name=hashtag)
            
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return VideoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VideoUpdateSerializer
        return VideoSerializer
    
    def perform_create(self, serializer):
        """
        Set the user when creating a video
        """
        video = serializer.save(user=self.request.user)
        
        # Trigger video processing
        process_video.delay(video.id)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """
        Like/unlike a video
        """
        video = self.get_object()
        user = request.user
        
        # Check if the user has already liked the video
        like, created = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(Video),
            object_id=video.id
        )
        
        if not created:
            # User already liked, so unlike
            like.delete()
            video.like_count = F('like_count') - 1
            video.save()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        
        # User liked the video
        video.like_count = F('like_count') + 1
        video.save()
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def record_view(self, request, pk=None):
        """
        Record a video view
        """
        video = self.get_object()
        serializer = VideoViewSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save(video=video)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def for_you(self, request):
        """
        Return personalized feed of videos (for the "For You" page)
        """
        # Basic implementation for now, can be enhanced with recommendation logic
        queryset = self.get_queryset().order_by('-created_at')[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def following(self, request):
        """
        Return videos from users that the current user follows
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Get users that the current user follows
        following_ids = request.user.following.values_list('to_user_id', flat=True)
        
        # Get videos from those users
        queryset = self.get_queryset().filter(user_id__in=following_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for hashtags
    """
    queryset = VideoHashtag.objects.all()
    serializer_class = VideoHashtagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        """
        Return hashtags based on filters
        """
        queryset = VideoHashtag.objects.all()
        
        # Order by video count by default
        return queryset.order_by('-video_count')
    
    @action(detail=True, methods=['get'])
    def videos(self, request, pk=None):
        """
        Return videos for a specific hashtag
        """
        hashtag = self.get_object()
        videos = Video.objects.filter(
            hashtag_relations__hashtag=hashtag,
            visibility='public',
            processing_status='ready'
        )
        
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Return trending hashtags
        """
        # Get hashtags used in videos from the last 7 days
        trending = VideoHashtag.objects.filter(
            video_relations__video__created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).annotate(
            recent_count=Count('video_relations')
        ).order_by('-recent_count')[:10]
        
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)
