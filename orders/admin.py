from django.contrib import admin
from .models import Category, Food, Customer, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "available")
    list_filter = ("category", "available")
    search_fields = ("name",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("line_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "created_at", "total")
    list_filter = ("status", "created_at")
    search_fields = ("customer__name", "customer__phone")
    inlines = [OrderItemInline]
