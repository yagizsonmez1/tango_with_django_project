from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),  # Maps to /rango/
    path('about/', views.about, name='about'),  # Maps to /rango/about/
]