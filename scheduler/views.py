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

def login_view(request):
    return render(request, 'scheduler/login.html', {})

@login_required
def editor(request):
    # Handle GET request for fetching class details
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'getClass' in request.GET:
        class_id = request.GET.get('editClassId')
        try:
            class_schedule = ClassSchedule.objects.get(id=class_id, subject__user=request.user)
            return JsonResponse({
                'success': True,
                'class': {
                    'id': class_schedule.id,
                    'subject_id': class_schedule.subject.id,
                    'day_of_week': class_schedule.day_of_week,
                    'start_time': class_schedule.start_time.strftime('%H:%M'),
                    'end_time': class_schedule.end_time.strftime('%H:%M')
                }
            })
        except ClassSchedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Class not found.'})
    
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
        elif 'editSubjectSelect' in request.POST:
            class_id = request.POST.get('editClassId')
            if not class_id:
                return JsonResponse({'success': False, 'error': 'Class ID is required.'})
            try:
                edit_class = ClassSchedule.objects.get(id=class_id, subject__user=request.user)
                subject_id = request.POST.get('editSubjectSelect')
                try:
                    subject = Subject.objects.get(id=subject_id, user=request.user)
                    edit_class.subject = subject
                except Subject.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Invalid subject selected.'})
                edit_class.day_of_week = request.POST.get('editClassDay')
                edit_class.start_time = request.POST.get('editStartTime')
                edit_class.end_time = request.POST.get('editEndTime')
                edit_class.save()
                return JsonResponse({'success': True, 'message': 'Class updated successfully.'})
                
            except ClassSchedule.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Class not found.'})
        
    
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
