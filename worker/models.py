# import uuid
# from django.db import models
# from django.utils import timezone
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from job.models import Job, CategoryJob, Region, City
# from token_manegers.models import CustomAccessToken
#
# class UserManager(BaseUserManager):
#     def create_user(self, phone, password=None, **extra_fields):
#         if not phone:
#             raise ValueError('The Phone number is required')
#         user = self.model(phone=phone, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#
# class Worker(AbstractBaseUser, PermissionsMixin):
#     GENDER_CHOICES = [
#         ('Male', 'Erkak'),
#         ('Female', 'Ayol'),
#     ]
#
#     phone = models.CharField(max_length=15, unique=True)
#
#     full_name = models.CharField(max_length=255)
#     region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
#     city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
#     gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
#     job_category = models.ForeignKey(CategoryJob, on_delete=models.SET_NULL, blank=True, null=True)
#     job_id = models.ManyToManyField(Job)
#
#     passport_number = models.IntegerField(blank=True, null=True)
#     passport_scan = models.URLField(blank=True, null=True)
#     passport_back_scan = models.URLField(blank=True, null=True)
#     passport_scan_with_face = models.URLField(blank=True, null=True)
#     district = models.CharField(max_length=255, blank=True, null=True)
#
#     is_active = models.BooleanField(default=True)
#     description = models.TextField(blank=True, null=True)
#     avatar = models.ImageField(blank=True, null=True)
#     passport_seria = models.CharField(max_length=50, blank=True, null=True)
#     images = models.ImageField(blank=True, null=True)
#     # location = models.PointField(geography=True, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='accountant_worker_set',
#         blank=True,
#         help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='accountant_worker_set',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )
#
#
#     USERNAME_FIELD = 'phone'
#     REQUIRED_FIELDS = ['full_name']
#
#     objects = UserManager()
#
#     def __str__(self):
#         return self.phone
#
#     def generate_token(self):
#         token_value = str(uuid.uuid4())
#         CustomAccessToken.objects.create(
#             token=token_value,
#             user=self,
#             user_type='worker',  # `user_type` ni worker sifatida belgilash
#             expires=timezone.now() + timezone.timedelta(days=7)  # Token muddati
#         )
#         print("Token yaratildi")
#         return token_value
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)  # Obyektni saqlash
#
#         # Yangi yaratilgan bo'lsa, token yaratish
#         if not CustomAccessToken.objects.filter(user=self).exists():
#             self.generate_token()
#
#     class Meta:
#         verbose_name = 'Worker'
#         verbose_name_plural = 'Workers'
#         ordering = ['created_at']
