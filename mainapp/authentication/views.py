
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
class RoleBasedLoginView(LoginView):
    template_name = 'authentication/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'role'):
            if user.role == 'store_manager':
                return '/inventory/'
            elif user.role == 'sales_staff':
                return '/orders/'
        return super().get_success_url()
from .forms import CustomUserCreationForm

from django.urls import reverse
from verify.models import EmailVerification
from django.core.mail import send_mail

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email verification
            user.save()
            # Create verification token and send email
            ev, _ = EmailVerification.objects.get_or_create(user=user)
            url = request.build_absolute_uri(reverse('verify:verify', args=[str(ev.token)]))
            send_mail(
                'Verify your email',
                f'Click the link to verify your account: {url}',
                None,
                [user.email],
            )
            return render(request, 'verify/verify_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/signup.html', {'form': form})
