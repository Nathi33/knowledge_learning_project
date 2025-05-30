from django.urls import path
from .views import register_view, CustomLoginView, activate, CustomLogoutView, confirm_activation

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),  
    path('register/', register_view, name='register'),  
    path('logout/', CustomLogoutView.as_view(), name='logout'),   
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('confirm_activation/', confirm_activation, name='confirm_activation'),  
]