from django.contrib import admin

from .models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'created',
        'updated',
        'is_active',
    )
    list_filter = ('created', 'updated', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
