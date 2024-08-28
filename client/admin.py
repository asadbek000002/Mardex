from django.contrib import admin
from client.models import Order
#
#
# class ClientAdmin(BaseUserAdmin):
#     # Model uchun qaysi maydonlar admin panelda ko'rsatiladi
#     model = Client
#     list_display = ('phone', 'full_name', 'region', 'city')
#     list_filter = ('is_active', 'region', 'city')
#     search_fields = ('phone', 'full_name')
#     ordering = ('-created_at',)
#
#     # Quyidagi bo'limlar uchun maydonlarni belgilaydi
#     fieldsets = (
#         (None, {'fields': ('phone', 'full_name', 'password')}),
#         ('Personal info', {'fields': (
#             'region', 'city', 'description', 'avatar', 'passport_scan',
#             'passport_back_scan',
#             'passport_scan_with_face')}), #, 'location'
#         ('Permissions', {'fields': ('is_active',)}),
#
#     )
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('phone', 'full_name', 'password1', 'password2', 'city', 'region'),
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
# # Admin paneliga Worker modelini qo'shish
# admin.site.register(Client, ClientAdmin)
#
admin.site.register(Order)
