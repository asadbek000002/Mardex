from django.contrib import admin
from .models import AbstractUser

class AbstractUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'role', 'gender', 'is_superuser', 'is_active', 'created_at')
    list_filter = ('role', 'gender', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('full_name', 'phone')
    ordering = ('-created_at',)

admin.site.register(AbstractUser, AbstractUserAdmin)
