from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import CustomUser

_role_fieldset: tuple = (("LoreForge Role", {"fields": ("role",)}),)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = list(UserAdmin.fieldsets or []) + list(_role_fieldset)  # type: ignore[assignment,arg-type]
    add_fieldsets = list(UserAdmin.add_fieldsets or []) + list(_role_fieldset)  # type: ignore[assignment,arg-type]
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
