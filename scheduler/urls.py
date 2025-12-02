from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('editor/', views.editor, name='editor'),
    path('account/', views.account, name='account'),
    path('home/', views.home, name='home'),
    path("account/edit/", views.edit_profile_ajax, name="edit_profile_ajax"),

]
