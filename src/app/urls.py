from django.urls import path
from . import views


urlpatterns = [
    path('premium/', views.MainView.as_view(), name='premium'),
]
