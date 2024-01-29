
from django.contrib import admin
from .models import UserProfile, Product, Restaurant, Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

admin.site.register(Cart, CartAdmin)

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Restaurant)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)




