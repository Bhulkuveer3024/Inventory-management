# mainapp/orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Prefetch
from collections import Counter

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from inventory.models import Product

# ----------------------------
# Role-check function
# ----------------------------
def is_staff_or_admin(user):
    return user.role in ['staff', 'admin']

# ----------------------------
# Orders Views
# ----------------------------
@login_required
@user_passes_test(is_staff_or_admin)
def order_list(request):
    orders = Order.objects.prefetch_related(
        Prefetch("items", queryset=OrderItem.objects.all())
    ).order_by("-id")

    counts = {
        "total": orders.count(),
        "draft": orders.filter(status="DRAFT").count(),
        "pending": orders.filter(status="PENDING").count(),
        "paid": orders.filter(status="PAID").count(),
        "cancelled": orders.filter(status="CANCELLED").count(),
    }

    revenue = sum(
        sum(it.unit_price * it.quantity for it in o.items.all())
        for o in orders
    )

    return render(request, "orders/order_list.html", {"orders": orders, "counts": counts, "revenue": revenue})

@login_required
@user_passes_test(is_staff_or_admin)
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    return render(request, "orders/order_detail.html", {"order": order})

@login_required
@user_passes_test(is_staff_or_admin)
def order_create(request):
    order = Order()
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix="items")
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Save order and formset (ensure formset is bound to saved order)
                    order = form.save()
                    formset.instance = order
                    formset.save()
                    if order.status == "PAID":
                        _apply_stock_delta(order, deduct=True)
                messages.success(request, "Order created.")
                return redirect("orders:order_detail", pk=order.pk)
            except ValidationError as e:
                messages.error(request, f"{e}")
        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order, prefix="items")

    return render(
        request,
        "orders/order_form.html",
        {"form": form, "formset": formset, "is_create": True, "products": Product.objects.filter(is_active=True)},
    )

@login_required
@user_passes_test(is_staff_or_admin)
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    old_status = order.status
    old_counts = _snapshot_counts(order) if old_status == "PAID" else Counter()

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix="items")
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()

                    # Adjust stock based on status change
                    if old_status != order.status:
                        if order.status == "PAID" and old_status != "PAID":
                            _apply_stock_delta(order, deduct=True)
                        elif old_status == "PAID" and order.status in ("CANCELLED", "DRAFT"):
                            _apply_stock_delta(order, deduct=False)
                    else:
                        if order.status == "PAID":
                            new_counts = _snapshot_counts(order)
                            deltas = _compute_deltas(old_counts, new_counts)
                            if deltas:
                                _apply_stock_delta_partial(deltas)

                messages.success(request, "Order updated.")
                return redirect("orders:order_detail", pk=order.pk)
            except ValidationError as e:
                messages.error(request, f"{e}")
        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order, prefix="items")

    return render(
        request,
        "orders/order_form.html",
        {
            "form": form,
            "formset": formset,
            "is_create": False,
            "order": order,
            "products": Product.objects.filter(is_active=True),
        },
    )

@login_required
@user_passes_test(is_staff_or_admin)
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("orders:order_list")
    return render(request, "orders/order_confirm_delete.html", {"order": order})

# ----------------------------
# Stock helper functions
# ----------------------------
def _snapshot_counts(order):
    counts = Counter()
    for it in order.items.all():
        if it.product_id:
            counts[it.product_id] += it.quantity
    return counts

def _compute_deltas(old_counts, new_counts):
    all_ids = set(old_counts) | set(new_counts)
    deltas = {}
    for pid in all_ids:
        delta = new_counts.get(pid, 0) - old_counts.get(pid, 0)
        if delta != 0:
            deltas[pid] = delta
    return deltas

def _apply_stock_delta_partial(deltas):
    if not deltas:
        return
    pids = [pid for pid in deltas.keys() if pid]
    products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=pids)}

    # Validate availability for deductions first
    for pid, delta in deltas.items():
        if delta > 0 and products[pid].quantity < delta:
            raise ValidationError(f"Not enough stock for {products[pid].name}.")

    # Apply changes
    for pid, delta in deltas.items():
        p = products[pid]
        if delta > 0:
            p.quantity -= delta
        else:
            p.quantity += -delta
        p.save(update_fields=["quantity"])

def _apply_stock_delta(order: Order, deduct: bool):
    items = order.items.select_related("product")
    for it in items:
        if not it.product:
            raise ValidationError("All items must be linked to a Product to change stock.")
    if deduct:
        for it in items:
            if it.product.quantity < it.quantity:
                raise ValidationError(f"Not enough stock for {it.product.name}.")
    for it in items:
        p = it.product
        p.quantity = p.quantity - it.quantity if deduct else p.quantity + it.quantity
        p.save(update_fields=["quantity"])
