"""Cart and checkout views."""

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


def cart_detail(request):
    return render(
        request,
        "orders/cart.html",
        {"page_title": "Your Cart | AquaCare"},
    )


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if not product.in_stock:
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect(product.get_absolute_url())

    quantity = 1
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1

    cart = Cart(request)
    cart.add(product, quantity=quantity)
    messages.success(request, f"{product.name} added to your cart.")
    if request.POST.get("buy_now"):
        return redirect("orders:checkout")
    return redirect("orders:cart_detail")


def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        cart.remove(product)
        messages.info(request, f"{product.name} removed from your cart.")
    else:
        cart.add(product, quantity=quantity, override=True)
        messages.success(request, "Cart updated.")
    return redirect("orders:cart_detail")


def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Cart(request).remove(product)
    messages.info(request, f"{product.name} removed from your cart.")
    return redirect("orders:cart_detail")


def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        messages.warning(request, "Your cart is empty. Add a product to continue.")
        return redirect("products:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.customer = request.user
                order.save()
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        product_name=item["product"].name,
                        price=item["price"],
                        quantity=item["quantity"],
                    )
                    # Reduce stock so the catalogue stays accurate.
                    product = item["product"]
                    product.stock_quantity = max(
                        0, product.stock_quantity - item["quantity"]
                    )
                    product.save(update_fields=["stock_quantity", "updated_at"])
                order.recalculate_total()
            cart.clear()
            messages.success(request, f"Order {order.order_id} placed successfully!")
            return redirect("orders:order_success", order_id=order.order_id)
        messages.error(request, "Please correct the errors below.")
    else:
        form = CheckoutForm(user=request.user)

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "page_title": "Checkout | AquaCare"},
    )


def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(
        request,
        "orders/order_success.html",
        {"order": order, "page_title": f"Order {order.order_id} Confirmed | AquaCare"},
    )


def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    # Customers may only view their own orders; staff can view all.
    if order.customer and order.customer != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view that order.")
        return redirect("accounts:my_orders")
    return render(
        request,
        "orders/order_detail.html",
        {"order": order, "page_title": f"Order {order.order_id} | AquaCare"},
    )
