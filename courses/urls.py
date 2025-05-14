from django.urls import path
from .import views

urlpatterns = [
    path('', views.curriculum_list, name='curriculum_list'),
    path('theme/<int:theme_id>/', views.theme_detail, name='theme_detail'),
    path('curriculum/<int:curriculum_id>/', views.curriculum_detail, name='curriculum_detail'),
    path('curriculum/<int:curriculum_id>/purchase/', views.purchase_curriculum, name='purchase_curriculum'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
]