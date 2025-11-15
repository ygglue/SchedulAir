from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Subject, ClassSchedule
from .forms import SubjectForm, ClassScheduleForm

def home(response):
    return render(response, 'scheduler/home.html', {})

def editor(response):

    subjects = Subject.objects.all()
    return render(response, 'scheduler/editor.html', {'subjects': subjects})