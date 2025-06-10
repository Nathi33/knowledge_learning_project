from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from courses.models import Curriculum, Lesson
from payments.models import Payment
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

"""
Cart app views

This module manages the shopping cart functionalities including:
- Adding curriculum or lesson items to the cart with checks against already purchased items.
- Viewing the cart content with total price calculation.
- Removing items from the cart.
- Ensuring secure redirects after cart actions.

The cart is stored in the user session as a list of dictionaries, each representing an item
with type ('curriculum' or 'lesson'), id, title, price, and other metadata.

Key functions:
- get_purchased_items(user): Returns sets of purchased curriculum and lesson IDs.
- has_purchased_lessons_of_curriculum(payments_qs, curriculum): Checks if user purchased any lesson of a curriculum.
- redirect_secure(request, next_url=None): Redirects securely to a next URL or cart page.
- add_to_cart(request, item_id, item_type): POST, adds an item to the cart with validations.
- view_cart(request): Displays the cart and total price.
- remove_from_cart(request, item_id, item_type): GET, removes an item from the cart.
"""

def get_purchased_items(user):
    """
    Retrieve IDs of curriculums and lessons already purchased by the user.

    Args:
        user (User): The authenticated user instance.

    Returns:
        tuple: (set of purchased curriculum IDs, set of purchased lesson IDs)
    """
    payments = Payment.objects.filter(user=user, status='paid')
    purchased_curriculums_ids = set(payments.filter(curriculum__isnull=False).values_list('curriculum__id', flat=True))
    purchased_lessons_ids = set(payments.filter(lesson__isnull=False).values_list('lesson__id', flat=True))
    return purchased_curriculums_ids, purchased_lessons_ids

def has_purchased_lessons_of_curriculum(payments_qs, curriculum):
    """
    Check if the user has purchased at least one lesson from the given curriculum.

    Args:
        payments_qs (QuerySet): Payments queryset filtered for the user with status 'paid'.
        curriculum (Curriculum): Curriculum instance to check.

    Returns:
        bool: True if at least one lesson from the curriculum is purchased, False otherwise.
    """
    curriculum_lesson_ids_qs = curriculum.lessons.values_list('id', flat=True)
    return payments_qs.filter(lesson_id__in=curriculum_lesson_ids_qs).exists()

def redirect_secure(request, next_url=None):
    """
    Redirect securely to the provided next_url if valid, else to the cart page.

    Args:
        request (HttpRequest): The current HTTP request object.
        next_url (str, optional): URL to redirect to. Defaults to None.

    Returns:
        HttpResponseRedirect: Redirect response to next_url or 'cart' view.
    """
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
    """
    Add a curriculum or lesson item to the user's shopping cart stored in session.

    Validations:
    - Prevent adding items already purchased.
    - Prevent adding duplicate items.
    - Prevent mixing curriculum with its individual lessons in cart or purchases.

    Args:
        request (HttpRequest): The POST request containing user session and data.
        item_id (int or str): The ID of the curriculum or lesson to add.
        item_type (str): 'curriculum' or 'lesson'.

    Returns:
        HttpResponseRedirect: Redirects to 'next' URL if valid, else to cart page with appropriate messages.
    """
    cart = request.session.get('cart', [])
    next_url = request.POST.get('next')
    logger.debug(f"Ajout au panier demandé pour item_id={item_id}, item_type={item_type} par user={request.user.id}")

    payments = Payment.objects.filter(user=request.user, status='paid')
    purchased_curriculums_ids, purchased_lessons_ids = get_purchased_items(request.user)

    # Verification of purchase already made
    if item_type == 'curriculum':
        curriculum = get_object_or_404(Curriculum.objects.select_related('theme'), id=item_id)
        logger.debug(f"Chargement du cursus: {curriculum.title} (id={curriculum.id})")

        if curriculum.id in purchased_curriculums_ids:
            logger.info(f"L'utilisateur {request.user.id} a déjà acheté le cursus {curriculum.id}")
            messages.error(request, "Vous avez déjà acheté ce cursus.")
            return redirect_secure(request, next_url)
        
        if has_purchased_lessons_of_curriculum(payments, curriculum):
            logger.info(f"L'utilisateur {request.user.id} a déjà acheté une leçon du cursus {curriculum.id}")
            messages.error(request, "Vous avez déjà acheté une ou plusieurs leçons de ce cursus. Vous ne pouvez pas acheter le cursus complet.")
            return redirect_secure(request, next_url)
        
        # Check that the course is not already in the cart
        if any(str(item['id']) == str(item_id) and item['type'] == 'curriculum' for item in cart):
            logger.info(f"Cursus {curriculum.id} déjà dans le panier de l'utilisateur {request.user.id}")
            messages.error(request, "Ce cursus est déjà dans votre panier.")
            return redirect_secure(request, next_url)
        
        # Check that no lessons from the curriculum are already in the cart
        lesson_ids_in_cart = {item['id'] for item in cart if item['type'] == 'lesson'}
        curriculum_lesson_ids = set(curriculum.lessons.values_list('id', flat=True))
        if lesson_ids_in_cart.intersection(curriculum_lesson_ids):
            logger.info(f"Leçons du cursus {curriculum.id} déjà dans le panier. Refus d'ajout du cursus complet.")
            messages.error(request, "Une ou plusieurs leçons de ce cursus sont déjà dans votre panier. Vous ne pouvez pas ajouter le cursus complet.")
            return redirect_secure(request, next_url)
        
        # Add to cart
        cart.append({
            'type': 'curriculum',
            'id': curriculum.id,
            'title': curriculum.title,
            'price': curriculum.price,
            'theme': curriculum.theme.name
        })
        logger.info(f"Cursus {curriculum.id} ajouté au panier de l'utilisateur {request.user.id}")
    
    elif item_type == 'lesson':
        lesson = get_object_or_404(Lesson.objects.select_related('curriculum__theme'), id=item_id)
        logger.debug(f"Chargement de la leçon: {lesson.title} (id={lesson.id})")


        if lesson.id in purchased_lessons_ids:
            logger.info(f"L'utilisateur {request.user.id} a déjà acheté la leçon {lesson.id}")
            messages.error(request, "Vous avez déjà acheté cette leçon.")
            return redirect_secure(request, next_url)
        
        if lesson.curriculum_id in purchased_curriculums_ids:
            logger.info(f"L'utilisateur {request.user.id} a déjà acheté le cursus complet de la leçon {lesson.id}")
            messages.error(request, "Vous avez déjà acheté le cursus complet de cette leçon. Vous ne pouvez pas acheter la leçon séparément.")
            return redirect_secure(request, next_url)
        
        # Check that the lesson is not already in the cart
        if any(str(item['id']) == str(item_id) and item['type'] == 'lesson' for item in cart):
            logger.info(f"Leçon {lesson.id} déjà dans le panier de l'utilisateur {request.user.id}")
            messages.error(request, "Cette leçon est déjà dans votre panier.")
            return redirect_secure(request, next_url)
        
        # Check that the lesson curriculum is not already in the cart
        curriculum_ids_in_cart = {item['id'] for item in cart if item['type'] == 'curriculum'}
        if lesson.curriculum_id in curriculum_ids_in_cart:
            logger.info(f"Cursus de la leçon {lesson.id} déjà dans le panier de l'utilisateur {request.user.id}")
            messages.error(request, "Le cursus de cette leçon est déjà dans votre panier. Vous ne pouvez pas acheter la leçon séparément.")
            return redirect_secure(request, next_url)
        
        # Add to cart
        cart.append({
            'type': 'lesson',
            'id': lesson.id,
            'title': lesson.title,
            'price': lesson.price,
            'order': lesson.order,
            'curriculum': lesson.curriculum.title,
            'theme': lesson.curriculum.theme.name
        })
        logger.info(f"Leçon {lesson.id} ajoutée au panier de l'utilisateur {request.user.id}")
    
    else:
        logger.error(f"Type d'article non valide: {item_type}")
        messages.error(request, "Type d'article non valide.")
        return redirect_secure(request, next_url)
    
    # Saving the shopping cart in the session
    request.session['cart'] = cart
    logger.info(f"Panier mis à jour pour l'utilisateur {request.user.id}: {cart}")
    messages.success(request, "L'article a été ajouté au panier.")
    return redirect_secure(request, next_url)

def view_cart(request):
    """
    Render the shopping cart page with current cart items and total price.

    Args:
        request (HttpRequest): The current request object.

    Returns:
        HttpResponse: Rendered cart page with context data.
    """
    cart = request.session.get('cart', [])
    
    if request.user.is_authenticated:
        logger.info(f"Affichage du panier par l'utilisateur {request.user.id}. Contenu du panier : {cart}")
    else:
        logger.info(f"Affichage du panier par un utilisateur non authentifié. Contenu du panier : {cart}")


    total_price = sum(item['price'] for item in cart)
    logger.debug(f"Prix total du panier: {total_price}")
    
    return render(request, 'cart/cart.html', {
        'cart': cart, 
        'total_price': total_price,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@require_GET
def remove_from_cart(request, item_id, item_type):
    """
    Remove an item (curriculum or lesson) from the user's shopping cart in session.

    Args:
        request (HttpRequest): The current request object.
        item_id (int or str): ID of the item to remove.
        item_type (str): 'curriculum' or 'lesson'.

    Returns:
        HttpResponseRedirect: Redirects to the cart page with a success message.
    """
    logger.debug(f"Suppression de l'article demandé: item_id={item_id}, item_type={item_type} par user={request.user.id}")

    cart = request.session.get('cart', [])
    new_cart = []

    for item in cart:
        if not (str(item['id']) == str(item_id) and item['type'] == item_type):
            new_cart.append(item)
        else:
            logger.info(f"Article {item_id} de type {item_type} retiré du panier de l'utilisateur {request.user.id}")

    request.session['cart'] = new_cart
    messages.success(request, "L'article a été retiré du panier.")
    return redirect('cart')



    