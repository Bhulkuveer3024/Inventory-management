from django.shortcuts import render, get_object_or_404, redirect
from .forms import ProductForm
from .models import Product  
from django.contrib.auth.decorators import user_passes_test

def is_manager_or_admin(user):
    return user.role in ['store_manager', 'system_admin']

def is_staff_or_admin(user):
    return user.role in ['sales_staff', 'store_manager', 'system_admin']

def is_system_admin(user):
    return user.role == 'system_admin'

# Inventory views with role-based access
def product_list(request):
    """Public view of all products - no authentication required"""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'inventory/product_list.html', context)

def product_detail(request, pk):
    """Public view of individual product details - no authentication required"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/product_detail.html', {'product': product})

@user_passes_test(is_manager_or_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

@user_passes_test(is_manager_or_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

@user_passes_test(is_system_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_delete.html', {'product': product})

@user_passes_test(is_manager_or_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})
