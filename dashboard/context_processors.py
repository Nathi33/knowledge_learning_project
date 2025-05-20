from payments.models import Payment

# def has_paid_purchases(request):
#     if request.user.is_authenticated:
#         return {
#             'has_paid_purchases' : Payment.objects.filter(user=request.user, status='paid').exists()
#         }
#     return {'has_paid_purchases': False}
# def has_paid_purchases(request):
#     user = request.user
#     if user.is_authenticated:
#         from payments.models import Payment
#         paid_qs = Payment.objects.filter(user=user, status='paid')
#         print(f"[DEBUG] Paiements : {paid_qs}")
#         has_paid = paid_qs.exists()
#         return {'has_paid_purchases': has_paid}
#     return {'has_paid_purchases': False}
def has_paid_purchases(request):
    if request.user.is_authenticated:
        from payments.models import Payment
        paid_payments = Payment.objects.filter(user=request.user, status='paid')
        print(f"[DEBUG] Utilisateur : {request.user} (ID: {request.user.id})")
        print(f"[DEBUG] Paiements : {list(paid_payments)}")
        return {'has_paid_purchases': paid_payments.exists()}
    return {'has_paid_purchases': False}

