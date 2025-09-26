# urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect("login", permanent=False)),
    path("admin/", admin.site.urls),

    # path("", include(("two_factor.urls", "two_factor"), namespace="two_factor")),

    path("accounts/", include(("authentication.urls", "authentication"), namespace="authentication")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path("inventory/", include(("inventory.urls", "inventory"), namespace="inventory")),
]
