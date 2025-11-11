from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Subject, ClassSchedule
from .forms import SubjectForm, ClassScheduleForm

def add_schedule(request):
    subjects = Subject.objects.filter(user=request.user)
    return render(request, 'scheduler/')
