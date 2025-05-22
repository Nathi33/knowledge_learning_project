from django.urls import path
from . import views

urlpatterns = [
    path('certificate/<int:theme_id>/', views.view_certificate, name='view_certificate'),
]