from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from inventory.models import Product  

class Order(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING", "Pending Payment"),
        ("PAID", "Paid"),
        ("FULFILLED", "Fulfilled"),
        ("CANCELLED", "Cancelled"),
    ]
    class Meta:
        permissions = (
            ("can_fulfill_order", "Can mark orders as Fulfilled"),
            ("can_cancel_order", "Can cancel any order"),
            ("can_view_reports", "Can view sales reports"),
        )
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="order_items")
    product_name = models.CharField(max_length=255, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be at least 1.")

    def save(self, *args, **kwargs):
        if self.product:
            if not self.product_name:
                self.product_name = self.product.name
            if not self.unit_price or self.unit_price <= 0:
                self.unit_price = self.product.price
        super().save(*args, **kwargs)

    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name or (self.product.name if self.product else 'Item')} x{self.quantity}"
