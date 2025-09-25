from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    
    ROLE_CHOICES = [
        ('store_manager', 'Store Manager'),
        ('sales_staff', 'Sales Staff'),
        ('system_admin', 'System Administrator'),
    ]
    
    # Additional fields beyond default User model
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales_staff')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def has_manager_permissions(self):
        return self.role in ['store_manager', 'system_admin']
    
    def has_admin_permissions(self):
        return self.role == 'system_admin'