from django import forms
from django.forms import fields, widgets
from .models import ClassSchedule, Subject
from django.contrib.auth.models import User

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teacher']


class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = [
            'subject',
            'day_of_week',
            'start_time',
            'end_time',
        ]
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('usr', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['subject'].queryset = Subject.objects.filter(user=user)

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
