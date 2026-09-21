"""Authentication, customer dashboard and profile views."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from orders.models import Order
from quotations.models import Quotation
from services.models import AMCSubscription, ServiceRequest

from .forms import LoginForm, ProfileUpdateForm, RegisterForm, UserUpdateForm


def register(request):
    """Create a real user record in the database."""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"Welcome to AquaCare, {user.first_name}! Your account is ready."
            )
            return redirect("accounts:dashboard")
        messages.error(request, "Please fix the errors below to create your account.")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "page_title": "Create your AquaCare account"},
    )


class CustomLoginView(LoginView):
    """Login view that also accepts an email address as the username."""

    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("username", "")
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user:
                request.POST = request.POST.copy()
                request.POST["username"] = user.username
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Login | AquaCare"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Logged in successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username/email or password.")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:home")


@login_required
def dashboard(request):
    """Customer dashboard with orders, service requests and AMC overview."""
    orders = Order.objects.filter(customer=request.user)
    service_requests = ServiceRequest.objects.filter(customer=request.user)
    context = {
        "orders": orders[:5],
        "orders_count": orders.count(),
        "service_requests": service_requests[:5],
        "service_count": service_requests.count(),
        "installations": service_requests.filter(
            request_type=ServiceRequest.TYPE_INSTALLATION
        )[:5],
        "amc_subscriptions": AMCSubscription.objects.filter(customer=request.user),
        "quotations": Quotation.objects.filter(customer=request.user)[:5],
        "page_title": "My Dashboard | AquaCare",
    }
    return render(request, "dashboard/dashboard.html", context)


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
        messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        "dashboard/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "page_title": "My Profile | AquaCare",
        },
    )


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related("items")
    return render(
        request,
        "dashboard/my_orders.html",
        {"orders": orders, "page_title": "My Orders | AquaCare"},
    )


@login_required
def my_services(request):
    requests_qs = ServiceRequest.objects.filter(
        customer=request.user
    ).select_related("product", "technician")
    return render(
        request,
        "dashboard/my_services.html",
        {"service_requests": requests_qs, "page_title": "My Service Requests | AquaCare"},
    )


@login_required
def my_amc(request):
    return render(
        request,
        "dashboard/my_amc.html",
        {
            "subscriptions": AMCSubscription.objects.filter(
                customer=request.user
            ).select_related("plan"),
            "page_title": "My AMC | AquaCare",
        },
    )


@login_required
def my_quotations(request):
    return render(
        request,
        "dashboard/my_quotations.html",
        {
            "quotations": Quotation.objects.filter(customer=request.user),
            "page_title": "My Quotations | AquaCare",
        },
    )
