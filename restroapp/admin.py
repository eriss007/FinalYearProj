from django.contrib import admin
from .models import *



admin.site.register(
    [Admin, Customer, Category, Food, ShoppingCart, CartProduct, Order, FoodImage])



@admin.register(Review)
class Reviewadmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'food', 'rate', 'created_at']
    readonly_fields = ['created_at']