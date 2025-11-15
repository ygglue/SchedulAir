from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .models import Subject, ClassSchedule
from .forms import SubjectForm, ClassScheduleForm

def home(response):
    return render(response, 'scheduler/home.html', {})

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

            valid_start = datetime.strptime(start_time, "%H:%M").time()
            valid_end = datetime.strptime(end_time, "%H:%M").time()

            try:
                subject = Subject.objects.get(id=subject_id, user=request.user)
            except Subject.DoesNotExist:
                messages.error(request, "Invalid subject selected.")
                return redirect('editor')

            ClassSchedule.objects.create(
                subject=subject,
                day_of_week=day,
                start_time=valid_start,
                end_time=valid_end
            )

            messages.success(request, "Added successfully.")
            return redirect('editor')
        
    
    subjects = Subject.objects.all()
    return render(request, 'scheduler/editor.html', {'subjects': subjects})