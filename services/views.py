"""Service pages, booking forms, AMC plans and the technician dashboard."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .forms import AMCSubscribeForm, ServiceRequestForm, TechnicianStatusForm
from .models import AMCPlan, Service, ServiceRequest, Technician


def service_list(request):
    return render(
        request,
        "services/service_list.html",
        {
            "services": Service.objects.filter(is_active=True),
            "amc_plans": AMCPlan.objects.filter(is_active=True),
            "page_title": "Water Purifier Services | Installation, Repair & AMC",
            "meta_description": "AquaCare installation, repair, maintenance and AMC "
            "services for domestic, commercial and industrial water purifiers.",
        },
    )


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    return render(
        request,
        "services/service_detail.html",
        {
            "service": service,
            "other_services": Service.objects.filter(is_active=True).exclude(pk=service.pk),
            "page_title": f"{service.name} | AquaCare Services",
            "meta_description": service.short_description,
        },
    )


def book_service(request, request_type=ServiceRequest.TYPE_REPAIR):
    """Shared booking view for installation / repair / maintenance requests."""
    valid_types = dict(ServiceRequest.TYPE_CHOICES)
    if request_type not in valid_types:
        raise Http404("Unknown service type")

    initial = {"request_type": request_type}
    product_slug = request.GET.get("product")
    if product_slug:
        product = Product.objects.filter(slug=product_slug, is_active=True).first()
        if product:
            initial["product"] = product.pk

    if request.method == "POST":
        form = ServiceRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            service_request = form.save(commit=False)
            if request.user.is_authenticated:
                service_request.customer = request.user
            service_request.save()
            messages.success(
                request,
                f"Your request has been submitted. Reference: "
                f"{service_request.reference}. Our team will contact you shortly.",
            )
            if request.user.is_authenticated:
                return redirect("accounts:my_services")
            return redirect("services:track")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ServiceRequestForm(initial=initial, user=request.user)

    titles = {
        ServiceRequest.TYPE_INSTALLATION: "Book Installation",
        ServiceRequest.TYPE_REPAIR: "Request Repair / Service",
        ServiceRequest.TYPE_MAINTENANCE: "Book Maintenance",
        ServiceRequest.TYPE_AMC: "Book AMC Visit",
    }
    return render(
        request,
        "services/book_service.html",
        {
            "form": form,
            "heading": titles[request_type],
            "request_type": request_type,
            "page_title": f"{titles[request_type]} | AquaCare",
            "meta_description": f"{titles[request_type]} for your water purifier "
            "with AquaCare certified technicians.",
        },
    )


def book_installation(request):
    return book_service(request, ServiceRequest.TYPE_INSTALLATION)


def book_repair(request):
    return book_service(request, ServiceRequest.TYPE_REPAIR)


def book_maintenance(request):
    return book_service(request, ServiceRequest.TYPE_MAINTENANCE)


def amc_plans(request):
    return render(
        request,
        "services/amc_plans.html",
        {
            "plans": AMCPlan.objects.filter(is_active=True),
            "page_title": "AMC Plans | Annual Maintenance Contracts | AquaCare",
            "meta_description": "Compare AquaCare Basic, Standard and Premium annual "
            "maintenance contracts for water purifiers.",
        },
    )


@login_required
def amc_subscribe(request, slug=None):
    """Subscribe to an AMC plan (login required so we can link it to a customer)."""
    initial = {}
    if slug:
        plan = get_object_or_404(AMCPlan, slug=slug, is_active=True)
        initial["plan"] = plan.pk

    if request.method == "POST":
        form = AMCSubscribeForm(request.POST, user=request.user)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.customer = request.user
            subscription.save()
            messages.success(
                request,
                f"AMC request created ({subscription.reference}). "
                "Our team will confirm activation shortly.",
            )
            return redirect("accounts:my_amc")
        messages.error(request, "Please correct the errors below.")
    else:
        form = AMCSubscribeForm(initial=initial, user=request.user)

    return render(
        request,
        "services/amc_subscribe.html",
        {"form": form, "page_title": "Subscribe to an AMC Plan | AquaCare"},
    )


def track_service(request):
    """Public tracking by reference number (also useful for guest bookings)."""
    service_request = None
    reference = request.GET.get("reference", "").strip()
    if reference:
        service_request = ServiceRequest.objects.filter(
            reference__iexact=reference
        ).select_related("technician", "product").first()
        if not service_request:
            messages.error(request, "No service request found with that reference.")
    return render(
        request,
        "services/track.html",
        {
            "service_request": service_request,
            "reference": reference,
            "page_title": "Track Your Service Request | AquaCare",
        },
    )


# ---------------------------------------------------------------------------
# Technician dashboard
# ---------------------------------------------------------------------------
@login_required
def technician_dashboard(request):
    technician = Technician.objects.filter(user=request.user).first()
    if technician is None:
        messages.error(request, "Your account is not linked to a technician profile.")
        return redirect("core:home")

    jobs = technician.jobs.select_related("product", "customer")
    return render(
        request,
        "services/technician_dashboard.html",
        {
            "technician": technician,
            "jobs": jobs,
            "open_jobs": jobs.exclude(
                status__in=[ServiceRequest.STATUS_COMPLETED,
                            ServiceRequest.STATUS_CANCELLED]
            ),
            "status_form": TechnicianStatusForm(),
            "page_title": "Technician Dashboard | AquaCare",
        },
    )


@login_required
def technician_update_status(request, pk):
    technician = Technician.objects.filter(user=request.user).first()
    if technician is None:
        messages.error(request, "Your account is not linked to a technician profile.")
        return redirect("core:home")
    # A technician may only update jobs assigned to them.
    job = get_object_or_404(ServiceRequest, pk=pk, technician=technician)
    if request.method == "POST":
        form = TechnicianStatusForm(request.POST)
        if form.is_valid():
            job.status = form.cleaned_data["status"]
            job.save()
            messages.success(request, f"Job {job.reference} updated to {job.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selection.")
    return redirect("services:technician_dashboard")
