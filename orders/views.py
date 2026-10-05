from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, CustomerForm, FoodForm, OrderForm
from .models import Category, Customer, Food, Order, OrderItem


def dashboard(request):
    context = {
        "food_count": Food.objects.count(),
        "customer_count": Customer.objects.count(),
        "order_count": Order.objects.count(),
        "pending_count": Order.objects.filter(status="PENDING").count(),
        "recent_orders": Order.objects.select_related("customer").order_by("-created_at")[:10],
    }
    return render(request, "orders/dashboard.html", context)


# Category CRUD
def category_list(request):
    return render(request, "orders/category_list.html", {"categories": Category.objects.all()})


def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category created.")
        return redirect("category_list")
    return render(request, "orders/form.html", {"form": form, "title": "Add Category"})


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect("category_list")
    return render(request, "orders/form.html", {"form": form, "title": "Edit Category"})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("category_list")
    return render(request, "orders/confirm_delete.html", {"object": category, "back_url": "category_list"})


# Food CRUD
def food_list(request):
    foods = Food.objects.select_related("category")
    q = request.GET.get("q", "")
    if q:
        foods = foods.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    return render(request, "orders/food_list.html", {"foods": foods, "q": q})


def food_create(request):
    form = FoodForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Food item created.")
        return redirect("food_list")
    return render(request, "orders/form.html", {"form": form, "title": "Add Food"})


def food_update(request, pk):
    food = get_object_or_404(Food, pk=pk)
    form = FoodForm(request.POST or None, instance=food)
    if form.is_valid():
        form.save()
        messages.success(request, "Food item updated.")
        return redirect("food_list")
    return render(request, "orders/form.html", {"form": form, "title": "Edit Food"})


def food_delete(request, pk):
    food = get_object_or_404(Food, pk=pk)
    if request.method == "POST":
        food.delete()
        messages.success(request, "Food item deleted.")
        return redirect("food_list")
    return render(request, "orders/confirm_delete.html", {"object": food, "back_url": "food_list"})


# Customer CRUD
def customer_list(request):
    customers = Customer.objects.all()
    q = request.GET.get("q", "")
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(phone__icontains=q))
    return render(request, "orders/customer_list.html", {"customers": customers, "q": q})


def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer created.")
        return redirect("customer_list")
    return render(request, "orders/form.html", {"form": form, "title": "Add Customer"})


def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer updated.")
        return redirect("customer_list")
    return render(request, "orders/form.html", {"form": form, "title": "Edit Customer"})


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        messages.success(request, "Customer deleted.")
        return redirect("customer_list")
    return render(request, "orders/confirm_delete.html", {"object": customer, "back_url": "customer_list"})


# Orders
@transaction.atomic
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            food_ids = request.POST.getlist("food_id")
            quantities = request.POST.getlist("quantity")

            added = 0
            for food_id, quantity in zip(food_ids, quantities):
                try:
                    food = Food.objects.get(pk=food_id, available=True)
                    qty = int(quantity)
                    if qty > 0:
                        OrderItem.objects.create(
                            order=order,
                            food=food,
                            quantity=qty,
                            unit_price=food.price,
                        )
                        added += 1
                except (Food.DoesNotExist, ValueError):
                    continue

            if added == 0:
                transaction.set_rollback(True)
                form.add_error(None, "Add at least one available food item.")
            else:
                messages.success(request, f"Order #{order.id} created.")
                return redirect("order_detail", pk=order.id)
    else:
        form = OrderForm()

    foods = Food.objects.filter(available=True).select_related("category")
    return render(request, "orders/order_create.html", {
        "form": form,
        "foods": foods,
    })


def order_list(request):
    orders = Order.objects.select_related("customer").prefetch_related("items__food").order_by("-created_at")
    status = request.GET.get("status", "")
    if status:
        orders = orders.filter(status=status)
    return render(request, "orders/order_list.html", {
        "orders": orders,
        "status": status,
        "status_choices": Order.STATUS_CHOICES,
    })


def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__food"),
        pk=pk,
    )
    return render(request, "orders/order_detail.html", {"order": order})


def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        status = request.POST.get("status")
        valid_statuses = {choice[0] for choice in Order.STATUS_CHOICES}
        if status in valid_statuses:
            order.status = status
            order.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Order #{order.id} status updated.")
    return redirect("order_detail", pk=pk)
