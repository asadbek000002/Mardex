from django.contrib import admin
from job.models import CategoryJob, Job, Region, City

admin.site.register(CategoryJob)
admin.site.register(Job)
admin.site.register(Region)
admin.site.register(City)
