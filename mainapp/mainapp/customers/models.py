from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import Product
from orders.models import Order, OrderItem

User = get_user_model()

# You can extend this with customer-specific fields if needed
