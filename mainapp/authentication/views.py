from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # handle "next" param, otherwise go to dashboard
            next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()

    # Always render form if GET or invalid POST
    return render(request, 'authentication/login.html', {'form': form})


# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    role_redirects = {
        'system_admin': '/admin/',
        'store_manager': '/inventory/',
        'sales_staff': '/orders/',
    }
    redirect_url = role_redirects.get(request.user.role)
    if redirect_url:
        return redirect(redirect_url)
    return render(request, 'authentication/unauthorized.html', status=403)
