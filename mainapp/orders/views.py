
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.core.exceptions import ValidationError, PermissionDenied

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from inventory.models import Product


def has_order_access(user):
    return user.role in ['store_manager', 'sales_staff']


@login_required
@user_passes_test(has_order_access)
def order_list(request):
    if not has_order_access(request.user):
        return redirect('inventory:product_list')
    orders = Order.objects.prefetch_related(
        Prefetch("items", queryset=OrderItem.objects.all())
    ).order_by("-id")

from collections import Counter
from inventory.models import Product
@login_required
def order_list(request):
    orders = Order.objects.prefetch_related(Prefetch("items", queryset=OrderItem.objects.all())).order_by("-id")
    counts = {
        "total": orders.count(),
        "draft": orders.filter(status="DRAFT").count(),
        "pending": orders.filter(status="PENDING").count(),
        "paid": orders.filter(status="PAID").count(),
        "cancelled": orders.filter(status="CANCELLED").count(),
    }
    revenue = 0
    for o in orders:
        revenue += sum(it.unit_price * it.quantity for it in o.items.all())
    return render(request, "orders/order_list.html", {"orders": orders, "counts": counts, "revenue": revenue})

@login_required
@user_passes_test(has_order_access)
def order_detail(request, pk):
    if not has_order_access(request.user):
        return redirect('inventory:product_list')
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    return render(request, "orders/order_detail.html", {"order": order})

@login_required
@user_passes_test(has_order_access)
def order_create(request):
    if not has_order_access(request.user):
        return redirect('inventory:product_list')
    order = Order()
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix="items")
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    order = form.save()
                    formset.instance = order
                    formset.save()
                    if order.status == "PAID":
                        _apply_stock_delta(order, deduct=True)
                messages.success(request, "Order created.")
                return redirect("orders:detail", pk=order.pk)
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
        {"form": form, "formset": formset, "is_create": True, "products": Product.objects.filter(is_active=True)}
    )

@login_required
@user_passes_test(has_order_access)
def order_update(request, pk):
    if not has_order_access(request.user):
        return redirect('inventory:product_list')
def order_update(request, pk):
    """
    Edit an order. Adjust stock if:
    - status changes to PAID (deduct all)
    - status changes from PAID to DRAFT/CANCELLED (return all)
    - status stays PAID but items/quantities changed (apply deltas)
    """
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
                return redirect("orders:detail", pk=order.pk)
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
@user_passes_test(has_order_access)
def order_delete(request, pk):
    if not has_order_access(request.user):
        return redirect('inventory:product_list')
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("orders:list")
    return render(request, "orders/order_confirm_delete.html", {"order": order})


def _snapshot_counts(order):
    """
    Return a Counter mapping product_id -> total qty in this order.
    Only includes items that have a product.
    """
    counts = Counter()
    for it in order.items.all():
        if it.product_id:
            counts[it.product_id] += it.quantity
    return counts

def _compute_deltas(old_counts, new_counts):
    """
    Return {product_id: delta_qty}, where +delta means deduct, -delta means add back.
    """
    all_ids = set(old_counts) | set(new_counts)
    deltas = {}
    for pid in all_ids:
        delta = new_counts.get(pid, 0) - old_counts.get(pid, 0)
        if delta != 0:
            deltas[pid] = delta
    return deltas

def _apply_stock_delta_partial(deltas):
    """
    Apply per-product deltas:
      +N => deduct N from stock
      -N => add N back to stock
    Validates availability before deducting.
    """
    if not deltas:
        return
    pids = [pid for pid in deltas.keys() if pid]
    products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=pids)}

    for pid, delta in deltas.items():
        if delta > 0:
            p = products[pid]
            if p.quantity < delta:
                raise ValidationError(f"Not enough stock for {p.name}.")

    # Apply
    for pid, delta in deltas.items():
        p = products[pid]
        if delta > 0:
            p.quantity -= delta
        else:
            p.quantity += (-delta)
        p.save(update_fields=["quantity"])




@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("orders:list")
    return render(request, "orders/order_confirm_delete.html", {"order": order})

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
