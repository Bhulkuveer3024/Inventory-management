<<<<<<< HEAD
"""
URL configuration for main app project.
=======
# urls.py
>>>>>>> 440b0ee70f4c9c681cd9f43649f32987bc5ff347

from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from django.views.generic import RedirectView
handler403 = "mainapp.views.permission_denied"




from django.views.generic import RedirectView
from authentication.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('login/', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('auth/', include('authentication.urls')),
    path('inventory/', include('inventory.urls')),
    path('orders/', include('orders.urls')),
    path('customers/', include('customers.urls')),

]
=======
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
>>>>>>> 440b0ee70f4c9c681cd9f43649f32987bc5ff347
