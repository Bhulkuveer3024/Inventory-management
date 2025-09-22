# This maps URLs to our simple list/detail views.

# What this does: Routes for orders CRUD.
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="list"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("new/", views.order_create, name="create"),
    path("<int:pk>/edit/", views.order_update, name="update"),
    path("<int:pk>/delete/", views.order_delete, name="delete"),
]
