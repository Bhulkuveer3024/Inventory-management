"""
URL configuration for mainapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
handler403 = "mainapp.views.permission_denied"


urlpatterns = [
    path("", include("two_factor.urls", "two_factor")),
    path('admin/', admin.site.urls),
    path("accounts/", include("authentication.urls", namespace="authentication")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("inventory/", include("inventory.urls", namespace="inventory")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("", include("orders.urls", namespace="orders")),
]


urlpatterns = [
    path("admin/", admin.site.urls),

    # your custom auth app routes (signup/login pages you already have)

    # Django’s built-in auth helpers: password reset/change, etc.

    # apps
      # optional: home -> orders list
]