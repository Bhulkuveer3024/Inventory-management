# This shows a list of orders and a detail page.

from django.shortcuts import render, get_object_or_404
from .models import Order

def order_list(request):
    orders = Order.objects.all().order_by("-id")
    return render(request, "orders/order_list.html", {"orders": orders})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/order_detail.html", {"order": order})
