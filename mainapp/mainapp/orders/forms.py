from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from inventory.models import Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "customer_email", "status"]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "customer_email": forms.EmailInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        if inst and inst.pk and (not inst.unit_price or float(inst.unit_price) == 0) and inst.product_id:
            self.fields["unit_price"].initial = inst.product.price

    class Meta:
        model = OrderItem
        fields = ["product", "unit_price", "quantity"]
        widgets = {
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    fields=["product", "unit_price", "quantity"],
    extra=1,
    can_delete=True
)
