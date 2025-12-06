import requests
import json
from pathlib import Path
from django.conf import settings
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.core.cache import cache

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'

CURRENT_APP_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = CURRENT_APP_DIR.parent

JSON_FILE_PATH = PROJECT_ROOT / 'static' / 'json' / 'weather_code.json'

def get_weather_forecast(city):
    print('getting weather data')

    latitude = city[1] 
    longitude = city[2]
    if latitude and longitude:
        cache_key = f'weather_forecast_{latitude}_{longitude}'
        CACHE_TIMEOUT_SECONDS = get_seconds_until_midnight()

        cached_data = cache.get(cache_key)
        if cached_data:
            print(f'✓ Using cached data (cache expires at midnight)')
            return cached_data
        
        print(f'✗ No cached data found - fetching from API')

        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'weather_code,precipitation_sum,temperature_2m_max,temperature_2m_min',
            'hourly': 'temperature_2m,relative_humidity_2m,weather_code,apparent_temperature,dew_point_2m,precipitation_probability,wind_speed_10m',
            'timezone': 'auto',
            'timeformat': 'unixtime',
            'temperature_unit': 'celsius'
        }

        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            cache.set(cache_key, data, CACHE_TIMEOUT_SECONDS)
            midnight = datetime.now() + timedelta(seconds=CACHE_TIMEOUT_SECONDS)
            print(f'✓ Data cached until {midnight.strftime("%Y-%m-%d %H:%M:%S")}')
            return data

        except requests.exceptions.RequestException as e:
            print(f'API Request Error: {e}')
            return None
    else:
        with open(PROJECT_ROOT / 'static' / 'json' / 'example_weather_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
def get_seconds_until_midnight():
    """Calculates the seconds remaining until the end of the current day."""
    
    # Get the current local datetime
    now = datetime.now()
    
    # Get the datetime object for midnight tonight
    # This sets the time component to 00:00:00 and adds one day.
    midnight = datetime.combine(now.date() + timedelta(days=1), time())
    
    # Calculate the difference and return total seconds
    return int((midnight - now).total_seconds())


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

def get_weather_codes_lookup():
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f'ERROR: JSON file not found as {JSON_FILE_PATH}')
        return {}
    except json.JSONDecodeError:
        print(f"ERROR: JSON file is malformed or empty.")
        return {}
    
def get_icon_data(current_day:int, weather_code:list[int], is_day:bool = True):
    days_icons = []
    days_description = []

    code_data = get_weather_codes_lookup()

    for i in range(7):
        if i <= current_day:
            days_icons.append('')
            days_description.append('')
        else:
            if is_day:
                days_icons.append(code_data.get(str(weather_code[i-current_day])).get('day').get('image'))
                days_description.append(code_data.get(str(weather_code[i-current_day])).get('day').get('description'))
            else:
                days_description.append(code_data.get(str(weather_code[i-current_day])).get('day').get('description'))
                days_icons.append(code_data.get(str(weather_code[i-current_day])).get('night').get('image'))
    
    data = [days_icons, days_description]

    return data

            
