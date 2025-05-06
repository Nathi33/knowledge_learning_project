from django.urls import path
from .import views

urlpatterns = [
    path('', views.curriculum_list, name='curriculum_list'),
    path('curriculum/<int:curriculum_id>/', views.curriculum_detail, name='curriculum_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
]