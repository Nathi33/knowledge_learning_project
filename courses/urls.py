from django.urls import path
from .import views
from .views import import_data

urlpatterns = [
    path('', views.themes_list, name='themes_list'),
    path('theme/<int:theme_id>/', views.theme_detail, name='theme_detail'),
    path('curriculum/<int:curriculum_id>/', views.curriculum_detail, name='curriculum_detail'),
    path('curriculum/<int:curriculum_id>/purchase/', views.purchase_curriculum, name='purchase_curriculum'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('import-data/', import_data),
    path('theme/<int:theme_id>/edit/', views.edit_theme, name='edit_theme'),
    path('theme/<int:theme_id>/delete/', views.delete_theme, name='delete_theme'),
    path('themes/create/', views.create_theme, name='create_theme'),
]