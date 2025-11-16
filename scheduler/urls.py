from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='home'),
    path('editor/', views.editor, name='editor'),
    path('account/', views.account, name='account'),
    path('home/', views.home, name='landing'),
    path('login/', views.login_view, name='login'),
]
