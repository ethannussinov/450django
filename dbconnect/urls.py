from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard-data/', views.fetch_dashboard_data, name='dashboard_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
