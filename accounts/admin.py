from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import CustomerProfile


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = "Customer profile"


class UserAdmin(BaseUserAdmin):
    """Show the customer profile inline on the user page."""

    inlines = [CustomerProfileInline]
    list_display = ("username", "email", "first_name", "last_name",
                    "phone", "is_staff", "date_joined")
    list_filter = BaseUserAdmin.list_filter + ("date_joined",)

    @admin.display(description="Phone")
    def phone(self, obj):
        return getattr(obj.profile, "phone", "") if hasattr(obj, "profile") else ""


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "state", "pincode", "created_at")
    search_fields = ("user__username", "user__email", "phone", "city", "pincode")
    list_filter = ("city", "state")
