from django.contrib import admin
from .models import Product, Order, OrderItem, Expense


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "size", "color", "purchase_price", "selling_price", "stock_quantity", "is_active")
    list_filter = ("is_active", "size", "color")
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "created_at", "status", "total")
    list_filter = ("status",)
    search_fields = ("order_number",)
    inlines = [OrderItemInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "amount", "comment")
    list_filter = ("category", "date")