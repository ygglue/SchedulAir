from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('editor', views.editor, name='editor')
]