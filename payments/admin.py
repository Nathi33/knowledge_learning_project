from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'curriculum', 'lesson', 'amount', 'timestamp', 'status')
    readonly_fields = ('timestamp',)