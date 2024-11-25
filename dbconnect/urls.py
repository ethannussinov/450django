from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard-data/', views.fetch_dashboard_data, name='dashboard_data'),
    path('api/heatmap-data/', views.fetch_heatmap_data, name='heatmap_data'),
    path('api/get_district_data/', views.get_district_data, name='get_district_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
