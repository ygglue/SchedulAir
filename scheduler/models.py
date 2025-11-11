from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=50)
    teacher = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class ClassSchedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_schedule')
    day_of_week = models.CharField(
        max_length=10
        choices=[
            ('MON', 'Monday'),
            ('TUE', 'Tuesday'),
            ('WED', 'Wednesday'),
            ('THU', 'Thursday'),
            ('FRI', 'Friday'),
            ('SAT', 'Saturday'),
            ('SUN', 'Sunday'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.subject.name} - {self.day_of_week} ({self.start_time}-{self.end_time})"

