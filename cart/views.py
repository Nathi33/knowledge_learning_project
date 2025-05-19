from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from courses.models import Curriculum, Lesson
from payments.models import Payment
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

@require_POST
def add_to_cart(request, item_id, item_type):
    cart = request.session.get('cart', [])
    next_url = request.POST.get('next')

    def redirect_secure():
        if next_url and url_has_allowed_host_and_scheme(
            next_url, 
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect('cart')
    
    # Empêcher l'ajout d'un article déjà présent dans le panier
    for item in cart:
        if str(item['id']) == str(item_id) and item['type'] == item_type:
            messages.error(request, "Cet article est déjà dans votre panier.")
            return redirect_secure()

    # Ajout de l'article au panier    
    if item_type == 'curriculum':
        curriculum = get_object_or_404(Curriculum.objects.select_related('theme'), id=item_id)

        # Vérifie si une des leçons de ce cursus est déjà dans le panier
        lesson_ids_in_cart = [item['id'] for item in cart if item['type'] == 'lesson']
        curriculum_lesson_ids = curriculum.lessons.values_list('id', flat=True)

        if any(lesson_id in lesson_ids_in_cart for lesson_id in curriculum_lesson_ids):
            messages.error(request, "Une ou plusieurs leçons de ce cursus sont déjà dans votre panier. Vous ne pouvez pas ajouter ce cursus.")
            return redirect_secure()
        
        # Sinon ajout du cursus au panier
        cart.append({
            'type': 'curriculum',
            'id': curriculum.id, 
            'title': curriculum.title, 
            'price': curriculum.price,
            'theme': curriculum.theme.name if curriculum.theme else "Thème inconnu"
        })
       
    elif item_type == 'lesson':
        lesson = get_object_or_404(Lesson.objects.select_related('curriculum__theme'), id=item_id)

        # Vérifie si le cursus de cette leçon est déjà dans le panier
        curriculum_ids_in_cart = [item['id'] for item in cart if item['type'] == 'curriculum']
        if lesson.curriculum_id in curriculum_ids_in_cart:
            messages.error(request, "Le cursus de cette leçon est déjà dans votre panier. Vous ne pouvez pas ajouter cette leçon individuellement.")
            return redirect_secure()
        
        # Sinon ajout de la leçon au panier
        cart.append({
            'type': 'lesson', 
            'id': lesson.id, 
            'title': lesson.title, 
            'price': lesson.price,
            'order': lesson.order,
            'curriculum': lesson.curriculum.title if lesson.curriculum else "Cursus inconnu",
            'theme': lesson.curriculum.theme.name if lesson.curriculum and lesson.curriculum.theme else "Thème inconnu"
        })

    # Mise à jour de la session avec les articles du panier
    request.session['cart'] = cart
    messages.success(request, "L'article a été ajouté au panier.")
    return redirect_secure()


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



    