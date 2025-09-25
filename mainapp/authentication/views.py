
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser

def home_view(request):
    """Home view that redirects to login page"""
    return redirect('authentication:login')

def signup_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('authentication:dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to dashboard, which will handle role-based redirect
            return redirect('authentication:dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('authentication:login')

@login_required
def dashboard(request):
    """Dashboard view with role-based redirects"""
    user = request.user
    
    # Role-based redirects
    if user.role == 'system_admin':
        return redirect('admin:index')  # Redirect to Django admin
    elif user.role == 'store_manager':
        return redirect('inventory:product_list')  # Redirect to inventory management
    elif user.role == 'sales_staff':
        return redirect('orders:list')  # Redirect to orders
    else:
        # Fallback for any other roles
        return redirect('inventory:product_list')
from django.shortcuts import render

# Create your views here.
