from django import forms
from .models import Category, Food, Customer, Order

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ["category", "name", "description", "price", "available"]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "status", "notes"]
