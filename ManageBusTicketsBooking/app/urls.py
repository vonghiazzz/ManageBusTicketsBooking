from django.urls import path, include
from . import views
from .admin import admin_site


urlpatterns = [
    path('admin/',admin_site.urls, name="admin"),
    path('', views.index, name="home"),
    path('test/', views.test, name="test"),
    path('about_us/', views.aboutUs, name="about_us"),
    path('search/', views.search, name="search"),
    path('schedule/', views.schedule, name="schedule"),
    path('chatBox/', views.chatBox, name="chatBox"),

    path('profile/', views.profile, name="profile"),
    path('history/', views.history, name="history"),

    path('login/', views.loginPage, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logoutPage, name="logout"), 
    path('social-auth/',include('social_django.urls', namespace='social')),
    path('booking/<int:trip_id>/', views.booking, name='booking'),

]