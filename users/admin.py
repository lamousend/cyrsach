from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (("Роль в MAI Space", {"fields": ("role",)}),)
    list_display = ("username", "last_name", "first_name", "email", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")