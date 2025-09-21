from django.contrib import admin

# Register your models here.
# This makes Order + OrderItem editable in the Django admin.

from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "status", "created_at", "updated_at", "total")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "customer_email")
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "unit_price", "quantity")
