from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import login
from .models import EmailVerification

def send_verification(request):
    if not request.user.is_authenticated:
        return redirect("authentication:login")
    ev, _ = EmailVerification.objects.get_or_create(user=request.user)
    url = request.build_absolute_uri(reverse("verify:verify", args=[str(ev.token)]))
    send_mail("Verify your email", f"Click to verify: {url}", None, [request.user.email])
    return render(request, "verify/verify_sent.html")

def verify(request, token):
    ev = get_object_or_404(EmailVerification, token=token)
    if ev.is_valid():
        u = ev.user
        u.is_active = True   
        u.save()
        login(request, u)
        return render(request, "verify/verify_success.html")
    return render(request, "verify/verify_expired.html", status=400)
