from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('order/', views.place_order, name='place_order'),
    path('orders/', views.order_history, name='order_history'),
]
