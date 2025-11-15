from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .models import Subject, ClassSchedule
from .forms import SubjectForm, ClassScheduleForm

@login_required
def home(request):
    return render(request, 'scheduler/home.html', {})

def landing(request):
    return render(request, 'scheduler/landing.html', {})

@login_required
def account(request):
    return render(request, 'scheduler/account.html', {}) 

@login_required
def editor(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'instructor' in request.POST:
            name = request.POST.get('subjectName')
            teacher = request.POST.get('instructor')
            if name and teacher:
                subject = Subject.objects.create(user=request.user, name=name, teacher=teacher)
                return JsonResponse({
                    'success': True,
                    'subject': {
                        'id': subject.id,
                        'name': subject.name,
                        'teacher': subject.teacher
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'All fields are required.'})
        elif 'subjectSelect' in request.POST:
            subject_id = request.POST.get('subjectSelect')
            if not subject_id:
                messages.error(request, "Please select a subject.")
                return redirect('editor')
            day = request.POST.get('classDay')
            start_time = request.POST.get('startTime')
            end_time = request.POST.get('endTime')

            try:
                subject = Subject.objects.get(id=subject_id, user=request.user)
            except Subject.DoesNotExist:
                messages.error(request, "Invalid subject selected.")
                return redirect('editor')

            ClassSchedule.objects.create(
                subject=subject,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time
            )

            messages.success(request, "Added successfully.")
            return redirect('editor')
        
    
    current_date = datetime.now().strftime("%A, %B %d")
    current_day_abbr = datetime.now().strftime("%a")
    subjects = Subject.objects.filter(user=request.user)
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    sun_classes = ClassSchedule.objects.filter(day_of_week="SUN", subject__user=request.user).order_by('start_time')
    mon_classes = ClassSchedule.objects.filter(day_of_week="MON", subject__user=request.user).order_by('start_time')
    tue_classes = ClassSchedule.objects.filter(day_of_week="TUE", subject__user=request.user).order_by('start_time')
    wed_classes = ClassSchedule.objects.filter(day_of_week="WED", subject__user=request.user).order_by('start_time')
    thu_classes = ClassSchedule.objects.filter(day_of_week="THU", subject__user=request.user).order_by('start_time')
    fri_classes = ClassSchedule.objects.filter(day_of_week="FRI", subject__user=request.user).order_by('start_time')
    sat_classes = ClassSchedule.objects.filter(day_of_week="SAT", subject__user=request.user).order_by('start_time')
    return render(request, 'scheduler/editor.html', {
        'current_date': current_date,
        'current_day_abbr': current_day_abbr,
        'days_of_week': days_of_week,
        'subjects': subjects, 
        'sun_classes': sun_classes,
        'mon_classes': mon_classes, 
        'tue_classes': tue_classes,
        'wed_classes': wed_classes,
        'thu_classes': thu_classes,
        'fri_classes': fri_classes,
        'sat_classes': sat_classes,
    })
