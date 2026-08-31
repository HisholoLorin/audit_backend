from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('full_name', 'avatar_url')}),
    )
    list_display = ('username', 'email', 'full_name', 'is_staff')
