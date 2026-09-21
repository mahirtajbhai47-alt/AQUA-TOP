from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "full_name", "phone", "city", "total_amount",
                    "payment_method", "payment_status", "status", "created_at")
    list_editable = ("payment_status", "status")
    list_filter = ("status", "payment_status", "payment_method", "created_at")
    search_fields = ("order_id", "full_name", "phone", "email", "address")
    readonly_fields = ("order_id", "total_amount", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "price", "quantity", "subtotal")
    search_fields = ("order__order_id", "product_name")
