from django.urls import path
from .import views

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cart-success/', views.cart_success, name='cart_success'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]