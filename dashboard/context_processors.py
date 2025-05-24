from payments.models import Payment

def has_paid_purchases(request):
    """
    Checks if the authenticated user has any completed (paid) payments.

    Args:
        request (HttpRequest): The incoming HTTP request object.

    Returns:
        dict: A context dictionary with the key 'has_paid_purchases' set to True
              if the user has at least one payment with status 'paid', otherwise False.
    """
    if request.user.is_authenticated:
        from payments.models import Payment
        paid_payments = Payment.objects.filter(user=request.user, status='paid')
        print(f"[DEBUG] Utilisateur : {request.user} (ID: {request.user.id})")
        print(f"[DEBUG] Paiements : {list(paid_payments)}")
        return {'has_paid_purchases': paid_payments.exists()}
    return {'has_paid_purchases': False}

