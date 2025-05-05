from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserSettings


class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'settings'


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    inlines = [UserSettingsInline]
    list_display = ['username', 'email', 'display_name', 'is_verified', 
                    'follower_count', 'video_count', 'is_staff']
    list_filter = ['is_verified', 'account_privacy', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'display_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'display_name', 'bio', 'profile_picture')}),
        (_('App info'), {'fields': ('follower_count', 'following_count', 'video_count', 'is_verified')}),
        (_('Privacy'), {'fields': ('account_privacy', 'notification_enabled')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


admin.site.register(User, UserAdmin)
