from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Product, Category
from django.db import models

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'product_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    ordering = ['name']
    
    def product_count(self, obj):
        count = obj.product_set.count()
        url = reverse('admin:inventory_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} products</a>', url, count)
    
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'sku', 
        'category', 
        'price', 
        'quantity', 
        'stock_status',
        'is_active', 
        'created_at'
    ]
    
    list_filter = [
        'category', 
        'is_active', 
        'created_at', 
        ('quantity', admin.filters.SimpleListFilter)
    ]
    
    search_fields = ['name', 'sku', 'description']
    
    list_editable = ['price', 'quantity', 'is_active']
    
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'stock_status_detail']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'cost'),
            'classes': ('collapse',)
        }),
        ('Stock Management', {
            'fields': ('quantity', 'min_stock_level'),
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_active',
        'mark_as_inactive',
        'bulk_price_update',
        'export_selected_products'
    ]
    
    # Custom methods
    def stock_status(self, obj):
        if obj.is_low_stock():
            return format_html(
                '<span style="color: red; font-weight: bold;">Low Stock</span>'
            )
        elif obj.quantity == 0:
            return format_html(
                '<span style="color: darkred; font-weight: bold;">Out of Stock</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">In Stock</span>'
            )
    
    stock_status.short_description = 'Stock Status'
    
    def stock_status_detail(self, obj):
        if obj.pk:  # Only show for existing objects
            total_value = obj.quantity * obj.cost
            return format_html(
                '<p><strong>Current Stock:</strong> {}</p>'
                '<p><strong>Minimum Level:</strong> {}</p>'
                '<p><strong>Stock Value:</strong> ${:.2f}</p>'
                '<p><strong>Status:</strong> {}</p>',
                obj.quantity,
                obj.min_stock_level,
                total_value,
                'Low Stock' if obj.is_low_stock() else 'Normal'
            )
        return "Save the product to see stock details"
    
    stock_status_detail.short_description = 'Stock Details'
    
    # Custom actions
    @admin.action(description='Mark selected products as active')
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} products were successfully marked as active.',
            messages.SUCCESS
        )
    
    @admin.action(description='Mark selected products as inactive')
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} products were successfully marked as inactive.',
            messages.SUCCESS
        )
    
    @admin.action(description='Export selected products to CSV')
    def export_selected_products(self, request, queryset):
        # This would redirect to a CSV export view
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            reverse('inventory:export_inventory_csv') + 
            f'?ids={",".join(map(str, selected))}'
        )
    
    # Override save_model to set created_by
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    # Custom list filter for low stock
    class LowStockFilter(admin.SimpleListFilter):
        title = 'Stock Level'
        parameter_name = 'stock_level'
        
        def lookups(self, request, model_admin):
            return (
                ('low', 'Low Stock'),
                ('out', 'Out of Stock'),
                ('normal', 'Normal Stock'),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'low':
                return queryset.filter(quantity__lte=models.F('min_stock_level'))
            elif self.value() == 'out':
                return queryset.filter(quantity=0)
            elif self.value() == 'normal':
                return queryset.filter(quantity__gt=models.F('min_stock_level'))
    
    list_filter = [
        'category', 
        'is_active', 
        'created_at',
        LowStockFilter
    ]

# Customize admin site headers
admin.site.site_header = "Inventory Management System"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Welcome to Inventory Management"