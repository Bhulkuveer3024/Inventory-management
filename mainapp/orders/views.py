# What this does: List/Detail/Create/Update/Delete for orders with inline items.
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet

def order_list(request):
    # Prefetch items so totals are fast
    orders = Order.objects.prefetch_related(
        Prefetch("items", queryset=OrderItem.objects.all())
    ).order_by("-id")

    # Simple “dashboard” summary
    counts = {
        "total": orders.count(),
        "draft": orders.filter(status="DRAFT").count(),
        "pending": orders.filter(status="PENDING").count(),
        "paid": orders.filter(status="PAID").count(),
        "fulfilled": orders.filter(status="FULFILLED").count(),
        "cancelled": orders.filter(status="CANCELLED").count(),
    }
    # Total revenue (sum of subtotals) in Python (simple & clear)
    revenue = 0
    for o in orders:
        revenue += sum(it.unit_price * it.quantity for it in o.items.all())

    return render(request, "orders/order_list.html", {
        "orders": orders,
        "counts": counts,
        "revenue": revenue,
    })

def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"), pk=pk
    )
    return render(request, "orders/order_detail.html", {"order": order})

def order_create(request):
    order = Order()
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix="items")
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Order created.")
            return redirect("orders:detail", pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order, prefix="items")
    return render(request, "orders/order_form.html", {"form": form, "formset": formset, "is_create": True})

def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix="items")
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Order updated.")
            return redirect("orders:detail", pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order, prefix="items")
    return render(request, "orders/order_form.html", {"form": form, "formset": formset, "is_create": False, "order": order})

def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("orders:list")
    return render(request, "orders/order_confirm_delete.html", {"order": order})
