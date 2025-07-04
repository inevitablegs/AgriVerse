from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from agriai import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plant_analysis', views.plant_analysis, name='plant_analysis'),
]