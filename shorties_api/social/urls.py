from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'follows', views.FollowViewSet, basename='follow')
router.register(r'likes', views.LikeViewSet, basename='like')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'shares', views.ShareViewSet, basename='share')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
