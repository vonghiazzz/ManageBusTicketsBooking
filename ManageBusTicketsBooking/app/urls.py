from django.urls import path, include
from . import views
from .admin import admin_site


urlpatterns = [
    path('admin/',admin_site.urls, name="admin"),
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/<>', views.statistics, name='statistics'),


    path('', views.index, name="home"),
    path('about_us/', views.aboutUs, name="about_us"),
    path('search/', views.search, name="search"),
    path('schedule/', views.schedule, name="schedule"),
    path('passengerList/<int:trip_id>/', views.passengerList, name='passengerList'),

    path('change-password/', views.change_password, name='change_password'),
    path('send-otp/', views.send_otp_email, name='send_otp_email'),
    path('forrget-password/', views.formEmail, name='forrget_password'),
    path('schedule-driver/', views.scheduleDriver, name='scheduleDriver'),


    # path('chatBox/', views.chatBox, name="chatBox"),
    # path('report_vehicle/', views.report_vehicle, name='report_vehicle'),

    path('profile/', views.profile, name="profile"),
    path('history/', views.history, name="history"),

    # path('reportVehicle/', views.reportVehicle, name="reportVehicle"),
    # path('reportVehicle/<int:bus_id>/', views.reportVehicle, name='reportVehicle'),
    path('reportVehicle/<int:bus_id>/<int:trip_id>/', views.reportVehicle, name='reportVehicle'),

    path('feedback/<int:trip_id>/', views.feedback, name='feedback'),
    path('feedback/', views.feedbackAdmin, name='feedbackAdmin'),
    path('overviewFeedback/', views.overviewFeedback, name='overviewFeedback'),

    # path('custom_add_feedback/', views.custom_add_feedback, name='custom_add_feedback'),


    path('confirm/', views.confirm, name="confirm"),
    path('download/<int:trip_id>/', views.download_customer_info, name='download_customer_info'),



    path('login/', views.loginPage, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logoutPage, name="logout"), 
    path('social-auth/',include('social_django.urls', namespace='social')),
    path('booking/<int:trip_id>/', views.booking, name='booking'),

]