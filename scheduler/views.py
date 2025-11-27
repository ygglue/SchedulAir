from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .models import Subject, ClassSchedule
import os, requests

@login_required
def home(request):
    user_city = request.user.profile.city.split('|')
    display_name = user_city[0].split(', ', 1)
    now = timezone.localtime().time()
    api_key = os.getenv('OPENWEATHER_API_KEY')
    openweather_url = 'https://api.openweathermap.org/data/2.5/weather'
    openweather_params = {
        'lat': user_city[1],
        'lon': user_city[2],
        'appid': api_key,
        'units': 'metric'
    }

    weather_data = requests.get(url=openweather_url, params=openweather_params).json()
    windspeed = float(weather_data.get('wind').get('speed')) * 3.6
    sunrise = datetime.fromtimestamp(weather_data.get('sys').get('sunrise')).strftime("%I:%M %p").lstrip("0")
    sunset = datetime.fromtimestamp(weather_data.get('sys').get('sunset')).strftime("%I:%M %p").lstrip("0")


    class_sched = ClassSchedule.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
    )

    if class_sched.exists():
        current_class = class_sched.first()
        time_remaining = get_time_remaining(current_class)
    else:
        current_class = 'No Class'
        time_remaining= ''


    return render(request, 'scheduler/home.html', {'current_class': current_class, 
                                                   'time_remaining': time_remaining, 
                                                   'city_displayname1': display_name[0], 
                                                   'city_displayname2': display_name[1], 
                                                   'weather_data': weather_data, 
                                                   'windspeed': windspeed,
                                                   'sunrise': sunrise,
                                                   'sunset': sunset})

def landing(request):
    return render(request, 'scheduler/landing.html', {})


def login_view(request):
    return render(request, 'scheduler/login.html', {})

@login_required
def account(request):
    cities = []
    user_profile = request.user.profile
    
    user_city = user_profile.city.split('|', 1)[0] or 'You have not selected you city yet...'

    if request.method == 'POST':
        if 'locationData' in request.POST:
            #pang update ng User.profile.city
            location_data = request.POST.get('locationData')
            user_profile.city = location_data
            user_profile.save()

        return redirect('account')

    if request.method == 'GET' and 'locationInput' in request.GET:
        #fetching city data via nominatim 
        query = request.GET.get('locationInput', '').strip()
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'city': query,
            'format': 'json',
            'addressdetails': 1,
            'limit': 5,
            
        }
        headers = {"User-Agent": os.getenv('NOMINATIM_USER_AGENT')}
        data = requests.get(url=url, params=params, headers=headers).json()

        for i in range(len(data)):
            cities.append(data[i])
        
    return render(request, 'scheduler/account.html', {'cities': cities, 'user_city': user_city}) 

def _parse_time_field(value):
    try:
        return datetime.strptime(value, '%H:%M').time()
    except (TypeError, ValueError):
        return None


def _has_conflict(user, day, start_time, end_time, exclude_id=None):
    schedules = ClassSchedule.objects.filter(
        day_of_week=day,
        subject__user=user
    )
    if exclude_id:
        schedules = schedules.exclude(id=exclude_id)
    return schedules.filter(
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exists()


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
            start_time_raw = request.POST.get('startTime')
            end_time_raw = request.POST.get('endTime')

            start_time = _parse_time_field(start_time_raw)
            end_time = _parse_time_field(end_time_raw)

            if not day or not start_time or not end_time:
                messages.error(request, "Please provide a valid day and time range.")
                return redirect('editor')

            if start_time >= end_time:
                messages.error(request, "End time must be later than start time.")
                return redirect('editor')

            try:
                subject = Subject.objects.get(id=subject_id, user=request.user)
            except Subject.DoesNotExist:
                messages.error(request, "Invalid subject selected.")
                return redirect('editor')

            if _has_conflict(request.user, day, start_time, end_time):
                messages.error(request, "This class overlaps with an existing schedule.")
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
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Class ID is required.'})
                messages.error(request, "Class ID is required.")
                return redirect('editor')
            try:
                edit_class = ClassSchedule.objects.get(id=class_id, subject__user=request.user)
                subject_id = request.POST.get('editSubjectSelect')
                try:
                    subject = Subject.objects.get(id=subject_id, user=request.user)
                    edit_class.subject = subject
                except Subject.DoesNotExist:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': 'Invalid subject selected.'})
                    messages.error(request, "Invalid subject selected.")
                    return redirect('editor')
                day = request.POST.get('editClassDay')
                start_time_raw = request.POST.get('editStartTime')
                end_time_raw = request.POST.get('editEndTime')

                start_time = _parse_time_field(start_time_raw)
                end_time = _parse_time_field(end_time_raw)

                if not day or not start_time or not end_time:
                    error_message = "Please provide a valid day and time range."
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, error_message)
                    return redirect('editor')

                if start_time >= end_time:
                    error_message = "End time must be later than start time."
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, error_message)
                    return redirect('editor')

                if _has_conflict(request.user, day, start_time, end_time, exclude_id=edit_class.id):
                    error_message = "This class overlaps with an existing schedule."
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, error_message)
                    return redirect('editor')

                edit_class.day_of_week = day
                edit_class.start_time = start_time
                edit_class.end_time = end_time
                edit_class.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, "Class updated successfully.")
                return redirect('editor')
                
            except ClassSchedule.DoesNotExist:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Class not found.'})
                messages.error(request, "Class not found.")
                return redirect('editor')
        elif 'deleteClassId' in request.POST:
            class_id = request.POST.get('deleteClassId')
            if class_id:
                try:
                    delete_class = ClassSchedule.objects.get(id=class_id, subject__user=request.user)
                    delete_class.delete()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, "Class deleted successfully.")
                    return redirect('editor')
                except ClassSchedule.DoesNotExist:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': 'Class not found.'})
                    messages.error(request, "Class not found.")
                    return redirect('editor')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Class ID is required.'})
            messages.error(request, "Class ID is required.")
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


def get_time_remaining(obj):
    now = timezone.localtime().time()
    today = timezone.localdate()

    now_dt = datetime.combine(today, now)

    # If event crosses midnight (e.g., 22:00 → 02:00)
    if obj.end_time < obj.start_time:
        # end_time is tomorrow
        end_dt = datetime.combine(today + datetime.timedelta(days=1), obj.end_time)
    else:
        end_dt = datetime.combine(today, obj.end_time)

    remaining = end_dt - now_dt

    # If time already passed today, remaining will be negative
    if remaining.total_seconds() < 0:
        return datetime.timedelta(0)

    minutes = int(remaining.total_seconds() // 60)

    # No negative minutes
    return max(minutes, 0)
