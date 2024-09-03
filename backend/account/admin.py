from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from .models import CustomUser
from import_export.admin import ImportExportModelAdmin
from .resources import CustomUserResource

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, DjangoUserAdmin):
    """Add additional fields to user admin page with import/export functionality."""
    resource_class = CustomUserResource  # 指定资源类
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "phone_number")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "name","role","grade","major_class")
    actions = ['delete_selected']  # Ensure bulk delete is enabled

class GroupProxy(Group):
    """Proxy model for Group. Dedicated for django-admin."""
    class Meta:
        """Declare model being proxy."""
        proxy = True
        verbose_name_plural = verbose_name = '用户组'

@admin.register(GroupProxy)
class MyGroupAdmin(DjangoGroupAdmin):
    """Grouping useradmin with groupadmin"""
    actions = ['delete_selected']  # Ensure bulk delete is enabled

admin.site.unregister(Group)  # Avoid multiple GroupAdmin