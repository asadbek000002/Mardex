import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import os
from django.utils import timezone
from job.models import CategoryJob, Job, Region, City
from users.models import AbstractUser


class Order(models.Model):
    STATUS_CHOICES = [
        ('stable', 'Stable'),
        ('success', 'Success'),
        ('cancel_client', 'Cancel by Client'),
        ('cancel_user', 'Cancel by User'),
    ]

    worker = models.ForeignKey(AbstractUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders_as_worker')
    accepted_workers = models.ManyToManyField(AbstractUser, related_name='accepted_orders')
    client = models.ForeignKey(AbstractUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='client')
    job_category = models.ForeignKey(CategoryJob, on_delete=models.SET_NULL, blank=True, null=True)
    job_id = models.ManyToManyField(Job)
    price = models.CharField(max_length=255, blank=True, null=True)
    desc = models.TextField(default="", blank=True, null=True)
    full_desc = models.TextField(default="", blank=True, null=True)
    work_count = models.IntegerField(default=1)
    # location = models.JSONField(default=dict)
    images = models.ImageField(upload_to='order_image/', blank=True, null=True)
    is_finish = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='stable'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.client} by {self.worker}"
