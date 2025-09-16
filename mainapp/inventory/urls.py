from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Product URLs
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    
    # Inventory Management URLs
    path('stock-adjustment/', views.stock_adjustment, name='stock_adjustment'),
    path('stock-adjustment/<int:pk>/', views.adjust_product_stock, name='adjust_product_stock'),
    path('low-stock-alert/', views.low_stock_alert, name='low_stock_alert'),
    
    # AJAX URLs for dynamic functionality
    path('ajax/check-sku/', views.check_sku_availability, name='check_sku_availability'),
    path('ajax/update-stock/', views.ajax_update_stock, name='ajax_update_stock'),
    path('ajax/product-search/', views.ajax_product_search, name='ajax_product_search'),
]

