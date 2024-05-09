from django.contrib import admin
from .models import Clothing, CartItem, Order, OrderItem

admin.site.register(Clothing)
admin.site.register(CartItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)