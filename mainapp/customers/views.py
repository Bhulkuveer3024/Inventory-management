from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from inventory.models import Product
from orders.models import Order, OrderItem
from orders.forms import OrderForm, OrderItemFormSet

@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'customers/product_list.html', {'products': products})

@login_required
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.customer_email = request.user.email
            order.customer_name = request.user.get_full_name() or request.user.username
            order.save()
            formset.instance = order
            formset.save()
            # Deduct stock if order is PAID
            from orders.views import _apply_stock_delta
            if order.status == "PAID":
                _apply_stock_delta(order, deduct=True)
            return redirect('customers:order_history')
    else:
        form = OrderForm()
        formset = OrderItemFormSet(prefix='items')
    return render(request, 'customers/place_order.html', {'form': form, 'formset': formset})

@login_required
def order_history(request):
    orders = Order.objects.filter(customer_email=request.user.email)
    return render(request, 'customers/order_history.html', {'orders': orders})
