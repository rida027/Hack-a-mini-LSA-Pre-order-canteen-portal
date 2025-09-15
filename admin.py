from django.contrib import admin
from .models import CustomerProfile, ShopOwnerProfile, Food, Order, OrderItem

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'roll_no']
    search_fields = ['name', 'roll_no', 'user__username']

@admin.register(ShopOwnerProfile)
class ShopOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop_name', 'user']
    search_fields = ['name', 'shop_name', 'user__username']

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'shop_owner']
    list_filter = ['available', 'shop_owner']
    search_fields = ['name', 'shop_owner__shop_name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'shop_owner', 'status', 'total_amount', 'order_time']
    list_filter = ['status', 'order_time']
    search_fields = ['customer__name', 'shop_owner__shop_name']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'food', 'quantity', 'item_status']
    list_filter = ['item_status']
