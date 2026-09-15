from django.contrib import admin

from .models import AMCPlan, AMCSubscription, Service, ServiceRequest, Technician


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "starting_price", "is_active", "order")
    list_editable = ("starting_price", "is_active", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "short_description")


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "area", "specialization",
                    "experience_years", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active", "area")
    search_fields = ("name", "phone", "email", "area", "specialization")


@admin.register(AMCPlan)
class AMCPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_months", "price", "number_of_services",
                    "filter_replacement", "emergency_service", "is_popular", "is_active")
    list_editable = ("price", "number_of_services", "filter_replacement",
                     "emergency_service", "is_popular", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "request_type", "name", "phone", "product",
                    "preferred_date", "technician", "status", "created_at")
    list_editable = ("technician", "status")
    list_filter = ("status", "request_type", "technician", "preferred_date")
    search_fields = ("reference", "name", "phone", "email", "address",
                     "problem_description")
    readonly_fields = ("reference", "created_at", "updated_at", "completed_at")
    autocomplete_fields = ("product",)
    fieldsets = (
        ("Request", {"fields": ("reference", "request_type", "service", "product",
                                "customer")}),
        ("Customer details", {"fields": ("name", "phone", "email", "address",
                                         "city", "pincode")}),
        ("Scheduling", {"fields": ("preferred_date", "preferred_time")}),
        ("Issue", {"fields": ("problem_description", "attachment")}),
        ("Handling", {"fields": ("technician", "status", "admin_notes",
                                 "completed_at", "created_at", "updated_at")}),
    )


@admin.register(AMCSubscription)
class AMCSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "plan", "start_date",
                    "end_date", "status")
    list_editable = ("status",)
    list_filter = ("status", "plan")
    search_fields = ("reference", "customer__username", "phone", "address")
    readonly_fields = ("reference",)
