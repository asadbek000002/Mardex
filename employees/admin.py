# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import Accountant
#
#
# class AccountantAdmin(BaseUserAdmin):
#     # Model uchun qaysi maydonlar admin panelda ko'rsatiladi
#     model = Accountant
#     list_display = ('role', 'phone', 'full_name', 'is_staff', 'is_superuser', 'is_active')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'gender')
#     search_fields = ('phone', 'full_name')
#     ordering = ('-created_at',)
#
#     # Quyidagi bo'limlar uchun maydonlarni belgilaydi
#     fieldsets = (
#         (None, {'fields': ('phone', 'full_name')}),
#         ('Personal info', {'fields': ('role', 'gender', 'city')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
#
#     )
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('phone', 'full_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
#         }),
#     )
#
#     # Parol o'rnatish va tekshirish uchun methodlar
#     def save_model(self, request, obj, form, change):
#         if not change:
#             # Yangi foydalanuvchi qo'shish
#             obj.set_password(form.cleaned_data.get('password1'))
#         super().save_model(request, obj, form, change)
#
#
# # Admin paneliga Accountant modelini qo'shish
# admin.site.register(Accountant, AccountantAdmin)
# # admin.site.register(Manager)
#
