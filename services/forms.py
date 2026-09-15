from django import forms

from core.forms import BootstrapFormMixin
from products.models import Product

from .models import AMCPlan, AMCSubscription, ServiceRequest

TIME_SLOTS = [
    ("09:00 AM - 12:00 PM", "09:00 AM - 12:00 PM"),
    ("12:00 PM - 03:00 PM", "12:00 PM - 03:00 PM"),
    ("03:00 PM - 06:00 PM", "03:00 PM - 06:00 PM"),
    ("06:00 PM - 08:00 PM", "06:00 PM - 08:00 PM"),
]


class ServiceRequestForm(BootstrapFormMixin, forms.ModelForm):
    """Single form used for installation / repair / maintenance bookings."""

    preferred_time = forms.ChoiceField(choices=TIME_SLOTS, label="Preferred time")

    class Meta:
        model = ServiceRequest
        fields = [
            "request_type", "product", "name", "phone", "email",
            "address", "city", "pincode", "preferred_date", "preferred_time",
            "problem_description", "attachment",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "problem_description": forms.Textarea(attrs={"rows": 4}),
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "problem_description": "Problem description / additional notes",
            "attachment": "Photo or video of the issue (optional)",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)
        self.fields["product"].required = False
        self.fields["product"].empty_label = "Select product (optional)"
        # Pre-fill contact details for logged-in customers.
        if user is not None and user.is_authenticated and not self.is_bound:
            profile = getattr(user, "profile", None)
            self.fields["name"].initial = user.get_full_name() or user.username
            self.fields["email"].initial = user.email
            if profile:
                self.fields["phone"].initial = profile.phone
                self.fields["address"].initial = profile.address
                self.fields["city"].initial = profile.city
                self.fields["pincode"].initial = profile.pincode


class AMCSubscribeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AMCSubscription
        fields = ["plan", "product", "phone", "address", "start_date", "notes"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].queryset = AMCPlan.objects.filter(is_active=True)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)
        self.fields["product"].required = False
        if user is not None and user.is_authenticated and not self.is_bound:
            profile = getattr(user, "profile", None)
            if profile:
                self.fields["phone"].initial = profile.phone
                self.fields["address"].initial = profile.full_address


class TechnicianStatusForm(forms.Form):
    """Technicians update the job status from their dashboard."""

    STATUS_CHOICES = [
        (ServiceRequest.STATUS_ACCEPTED, "Accepted"),
        (ServiceRequest.STATUS_ON_THE_WAY, "On the Way"),
        (ServiceRequest.STATUS_IN_PROGRESS, "In Progress"),
        (ServiceRequest.STATUS_COMPLETED, "Completed"),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES, widget=forms.Select(attrs={"class": "form-select"})
    )
