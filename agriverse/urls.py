from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from agriai import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('plant-analysis/', include('agriai.urls')),  # for our plant analysis feature
]