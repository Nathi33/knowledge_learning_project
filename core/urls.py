from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('under-construction/', views.under_construction, name='under_construction'),
]
