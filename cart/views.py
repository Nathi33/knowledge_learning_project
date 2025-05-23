from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from courses.models import Curriculum, Lesson
from payments.models import Payment
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.decorators import login_required

def get_purchased_items(user):
    """ Retourne deux sets d'IDs : cursus achetés et leçons achetées. """
    payments = Payment.objects.filter(user=user, status='paid')
    purchased_curriculums_ids = set(payments.filter(curriculum__isnull=False).values_list('curriculum__id', flat=True))
    purchased_lessons_ids = set(payments.filter(lesson__isnull=False).values_list('lesson__id', flat=True))
    return purchased_curriculums_ids, purchased_lessons_ids

def has_purchased_lessons_of_curriculum(payments_qs, curriculum):
    """ Vérifie si l'utilisateur a acheté au moins une leçon d'un cursus donné. """
    curriculum_lesson_ids_qs = curriculum.lessons.values_list('id', flat=True)
    return payments_qs.filter(lesson_id__in=curriculum_lesson_ids_qs).exists()

def redirect_secure(request, next_url=None):
    """ Redirection sécurisée vers next_url si valide, sinon vers la page 'cart' """
    if next_url and url_has_allowed_host_and_scheme(
        next_url, 
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect('cart')

@require_POST
@login_required
def add_to_cart(request, item_id, item_type):
    cart = request.session.get('cart', [])
    next_url = request.POST.get('next')
    payments = Payment.objects.filter(user=request.user, status='paid')

    purchased_curriculums_ids, purchased_lessons_ids = get_purchased_items(request.user)

    # Vérification d'achat déjà effectué
    if item_type == 'curriculum':
        curriculum = get_object_or_404(Curriculum.objects.select_related('theme'), id=item_id)

        if curriculum.id in purchased_curriculums_ids:
            messages.error(request, "Vous avez déjà acheté ce cursus.")
            return redirect_secure(request, next_url)
        
        if has_purchased_lessons_of_curriculum(payments, curriculum):
            messages.error(request, "Vous avez déjà acheté une ou plusieurs leçons de ce cursus. Vous ne pouvez pas acheter le cursus complet.")
            return redirect_secure(request, next_url)
        
        # Vérifie que le cursus n'estp as déjà dans le panier
        if any(str(item['id']) == str(item_id) and item['type'] == 'curriculum' for item in cart):
            messages.error(request, "Ce cursus est déjà dans votre panier.")
            return redirect_secure(request, next_url)
        
        # Vérification qu'aucune leçon du cursus n'est déjà dans le panier
        lesson_ids_in_cart = {item['id'] for item in cart if item['type'] == 'lesson'}
        curriculum_lesson_ids = set(curriculum.lessons.values_list('id', flat=True))
        if lesson_ids_in_cart.intersection(curriculum_lesson_ids):
            messages.error(request, "Une ou plusieurs leçons de ce cursus sont déjà dans votre panier. Vous ne pouvez pas ajouter le cursus complet.")
            return redirect_secure(request, next_url)
        
        # Ajout au panier
        cart.append({
            'type': 'curriculum',
            'id': curriculum.id,
            'title': curriculum.title,
            'price': curriculum.price,
            'theme': curriculum.theme.name
        })
    
    elif item_type == 'lesson':
        lesson = get_object_or_404(Lesson.objects.select_related('curriculum__theme'), id=item_id)

        if lesson.id in purchased_lessons_ids:
            messages.error(request, "Vous avez déjà acheté cette leçon.")
            return redirect_secure(request, next_url)
        
        if lesson.curriculum_id in purchased_curriculums_ids:
            messages.error(request, "Vous avez déjà acheté le cursus complet de cette leçon. Vous ne pouvez pas acheter la leçon séparément.")
            return redirect_secure(request, next_url)
        
        # Vérifie que la leçon n'est pas déjà dans le panier
        if any(str(item['id']) == str(item_id) and item['type'] == 'lesson' for item in cart):
            messages.error(request, "Cette leçon est déjà dans votre panier.")
            return redirect_secure(request, next_url)
        
        # Vérification que le cursus de la leçon n'est pas déjà dans le panier
        curriculum_ids_in_cart = {item['id'] for item in cart if item['type'] == 'curriculum'}
        if lesson.curriculum_id in curriculum_ids_in_cart:
            messages.error(request, "Le cursus de cette leçon est déjà dans votre panier. Vous ne pouvez pas acheter la leçon séparément.")
            return redirect_secure(request, next_url)
        
        # Ajout au panier
        cart.append({
            'type': 'lesson',
            'id': lesson.id,
            'title': lesson.title,
            'price': lesson.price,
            'order': lesson.order,
            'curriculum': lesson.curriculum.title,
            'theme': lesson.curriculum.theme.name
        })
    
    else:
        messages.error(request, "Type d'article non valide.")
        return redirect_secure(request, next_url)
    
    # Enregistrement du panier dans la session
    request.session['cart'] = cart
    messages.success(request, "L'article a été ajouté au panier.")
    return redirect_secure(request, next_url)

def view_cart(request):
    cart = request.session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    return render(request, 'cart/cart.html', {
        'cart': cart, 
        'total_price': total_price,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@require_GET
def remove_from_cart(request, item_id, item_type):
    cart = request.session.get('cart', [])
    new_cart = []

    for item in cart:
        if not (str(item['id']) == str(item_id) and item['type'] == item_type):
            new_cart.append(item)

    request.session['cart'] = new_cart
    messages.success(request, "L'article a été retiré du panier.")
    return redirect('cart')



    