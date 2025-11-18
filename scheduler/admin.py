from django.contrib import admin
from .models import ClassSchedule, Subject, Profile

admin.site.register(Subject)
admin.site.register(ClassSchedule)
admin.site.register(Profile)