from django.urls import path
from .import views

urlpatterns = [
    path('buy/lesson/<int:lesson_id>/', views.buy_lesson, name='buy_lesson'),
    path('curriculum/<int:curriculum_id>/process', views.process_payment, name='process_payment'),
]