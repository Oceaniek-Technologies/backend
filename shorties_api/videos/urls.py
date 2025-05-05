from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'videos', views.VideoViewSet, basename='video')
router.register(r'hashtags', views.HashtagViewSet, basename='hashtag')

urlpatterns = [
    path('', include(router.urls)),
]
