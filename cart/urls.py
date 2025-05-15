from django.urls import path
from . import views

urlpatterns = [
    path('add_to_cart/<item_id>/<item_type>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('process_cart_payment/', views.process_cart_payment, name='process_cart_payment'),
    path('remove_from_cart/<item_id>/<item_type>/', views.remove_from_cart, name='remove_from_cart'),
]