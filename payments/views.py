import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from .models import Payment
from courses.models import Lesson, Curriculum
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
import json
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Méthode non autorisée.")
    
    try:
        cart = request.session.get('cart', [])
        if not cart:
            return JsonResponse({'error': 'Le panier est vide.'}, status=400)
        
        line_items = []
        for item in cart:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item['title'],
                    },
                    'unit_amount': int(item['price'] * 100),
                },
                'quantity': 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/payments/cart-success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
            metadata={
                'user_id': request.user.id,
                'items': json.dumps(cart)
            }
        )

        return JsonResponse({'id': session.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_success(request):
    return render(request, 'payments/success.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponseBadRequest()
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        items = json.loads(metadata.get('items', '[]'))

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse("Utilisateur non trouvé.", status=404)
        
        for item in items:
            if item['type'] == 'lesson':
                try:
                    lesson = Lesson.objects.get(id=item['id'])
                    Payment.objects.create(
                        user=user,
                        lesson=lesson,
                        amount=lesson.price,
                        status='paid',
                        stripe_checkout_id=session['id']
                    )
                except Lesson.DoesNotExist:
                    continue
            elif item['type'] == 'curriculum':
                try:
                    curriculum = Curriculum.objects.get(id=item['id'])
                    Payment.objects.create(
                        user=user,
                        curriculum=curriculum,
                        amount=curriculum.price,
                        status='paid',
                        stripe_checkout_id=session['id']
                    )
                except Curriculum.DoesNotExist:
                    continue

    return HttpResponse(status=200)


@login_required
def cart_success(request):
    request.session['cart'] = []
    messages.success(request, "Votre paiement a été effectué avec succès.")
    
    return render(request, 'payments/success.html')





