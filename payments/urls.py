from django.urls import path
from .import views

urlpatterns = [
    path('buy/lesson/<int:lesson_id>/', views.buy_lesson, name='buy_lesson'),
]