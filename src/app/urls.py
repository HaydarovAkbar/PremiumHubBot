from django.urls import path
from . import views


urlpatterns = [
    path("device-register/", views.register_device, name="device-register"),
    path('signup/', views.signup_view, name='signup'),
    path('premium/', views.MainView.as_view(), name='premium'),
]
