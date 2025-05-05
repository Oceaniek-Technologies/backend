from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import UserSettings
from .serializers import (
    UserSerializer, UserPrivateSerializer, UserPublicSerializer,
    UserCreateSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    UserSettingsSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            user_id = self.kwargs.get('pk')
            if self.request.user.id == int(user_id):
                return UserPrivateSerializer
            return UserPublicSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the authenticated user's details
        """
        serializer = UserPrivateSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password
        """
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"status": "password changed successfully"}, 
                            status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user settings
    """
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only the settings for the authenticated user
        """
        return UserSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create settings linked to the authenticated user
        """
        serializer.save(user=self.request.user)


class SearchUsersView(generics.ListAPIView):
    """
    API endpoint for searching users
    """
    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Filter users based on search query parameter
        """
        query = self.request.query_params.get('q', '')
        if query:
            return User.objects.filter(username__icontains=query) | \
                   User.objects.filter(display_name__icontains=query)
        return User.objects.none()
