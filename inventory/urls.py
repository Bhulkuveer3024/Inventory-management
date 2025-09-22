from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Product URLs
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),  # <-- comma added here
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
]
