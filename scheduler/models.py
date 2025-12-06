from django.db import models
from django.contrib.auth.models import User

# for extending User, ex: I added a new field for the users location to be used for openweather
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.TextField(max_length=20, blank=True, default=", The user hasn't set their location yet.|||")

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=50)
    teacher = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class ClassSchedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_schedule')
    day_of_week = models.CharField(
        max_length=10,
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

    def __str__(self):
        return f"{self.subject.name} - {self.day_of_week} ({self.start_time}-{self.end_time})"

