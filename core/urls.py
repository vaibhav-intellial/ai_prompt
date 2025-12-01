from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.compare_boms, name='compare_boms'),
    path('result/<int:pk>/', views.comparison_result, name='comparison_result'),
    path('download-json/<int:pk>/', views.download_comparison_json, name='download_json'),
]
