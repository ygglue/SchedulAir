# SchedulAir

A smart scheduling app that integrates school timetables with real-time weather data. It helps students and teachers plan their days more effectively, from knowing when to bring an umbrella to optimizing outdoor classes.

**Live Demo:** [schedulair.pythonanywhere.com](https://schedulair.pythonanywhere.com/)

## Features

- Smart schedule management for school timetables
- Real-time weather integration
- Weather-based recommendations
- Responsive design for all devices

## Technology Stack

- Django (Python)
- HTML, CSS, JavaScript
- Weather API integration
- Deployed on PythonAnywhere

## Installation

1. Clone the repository
```bash
git clone https://github.com/ygglue/SchedulAir.git
cd SchedulAir
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Start the development server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.
