from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profile', views.UserViewSet, basename='user')
router.register(r'settings', views.UserSettingsViewSet, basename='user-settings')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.SearchUsersView.as_view(), name='user-search'),
]
