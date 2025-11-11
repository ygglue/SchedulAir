from django import forms
from django.forms import fields, widgets
from .models import ClassSchedule, Subject

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Math'}),
            'teacher' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ma'am Tine"}),
        }


class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = [
            'subject',
            'day_of_week',
            'start_time',
            'end_time',
            'room',
        ]
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room 101'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('usr', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['subject'].queryset = Subject.objects.filter(user=user)
