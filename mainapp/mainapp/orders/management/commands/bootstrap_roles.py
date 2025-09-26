from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from orders.models import Order, OrderItem
from inventory.models import Product, Category

def grant(group, *perms):
    for code in perms:
        p = Permission.objects.get(codename=code)
        group.permissions.add(p)

class Command(BaseCommand):
    help = "Create default roles (groups) and assign permissions"

    def handle(self, *args, **kwargs):
        admin_g, _ = Group.objects.get_or_create(name="System Admin")
        manager_g, _ = Group.objects.get_or_create(name="Store Manager")
        sales_g, _ = Group.objects.get_or_create(name="Sales Staff")

        # Built-in perms
        o_add, o_change, o_delete, o_view = [f"{p}_order" for p in ("add","change","delete","view")]
        oi_add, oi_change, oi_delete, oi_view = [f"{p}_orderitem" for p in ("add","change","delete","view")]
        p_add, p_change, p_delete, p_view = [f"{p}_product" for p in ("add","change","delete","view")]
        c_add, c_change, c_delete, c_view = [f"{p}_category" for p in ("add","change","delete","view")]

        # Custom perms
        can_fulfill = "can_fulfill_order"
        can_cancel = "can_cancel_order"
        can_reports = "can_view_reports"
        can_bulk_price = "can_bulk_update_prices"

        # System Admin = everything we care about
        grant(admin_g,
              o_add,o_change,o_delete,o_view,
              oi_add,oi_change,oi_delete,oi_view,
              p_add,p_change,p_delete,p_view,
              c_add,c_change,c_delete,c_view,
              can_fulfill,can_cancel,can_reports,can_bulk_price)

        # Store Manager
        grant(manager_g,
              o_view,o_change,oi_view,oi_change,  # manage orders
              p_view,p_change,                    # manage products (no delete)
              c_view,c_change,
              can_fulfill,can_reports)

        # Sales Staff
        grant(sales_g,
              o_view,o_add,o_change,             # create/update orders
              oi_view,oi_add,oi_change,
              p_view)                            # read product/stock

        self.stdout.write(self.style.SUCCESS("Roles & permissions bootstrapped."))
