# import uuid
#
# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.utils import timezone
#
#
#
# class AccountantManager(BaseUserManager):
#     use_in_migrations = True
#
#     def create_user(self, phone, full_name, password=None, **extra_fields):
#         """
#         Create and return a regular user with an email and password.
#         """
#         if not phone:
#             raise ValueError('The Phone field must be set')
#         if not full_name:
#             raise ValueError('The Full Name field must be set')
#
#         user = self.model(phone=phone, full_name=full_name, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, phone, full_name, password=None, **extra_fields):
#         """
#         Create and return a superuser with an email and password.
#         """
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#
#         return self.create_user(phone, full_name, password, **extra_fields)
#
#
# class Accountant(AbstractBaseUser, PermissionsMixin):
#     ROLE_CHOICES = [
#         ('Bosh buxgalter', 'Bosh buxgalter'),
#         ('buxgalter', 'buxgalter'),
#     ]
#
#     GENDER_CHOICES = [
#         ('Male', 'Erkak'),
#         ('Female', 'Ayol'),
#     ]
#
#     full_name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=15, unique=True)
#     city = models.CharField(max_length=255, blank=True)
#     role = models.CharField(max_length=50, choices=ROLE_CHOICES)
#     gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='accountant_user_set',
#         blank=True,
#         help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='accountant_user_set',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )
#
#
#
#     objects = AccountantManager()
#
#     USERNAME_FIELD = 'phone'
#     REQUIRED_FIELDS = ['full_name']
#
#
#
#     def __str__(self):
#         return self.full_name
#
#
#     class Meta:
#         verbose_name = 'Accountant'
#         verbose_name_plural = 'Accountants'
#         ordering = ['created_at']
