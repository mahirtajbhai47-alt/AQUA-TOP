from django import forms

from core.forms import BootstrapFormMixin
from products.models import Product
from services.models import Service

from .models import Quotation


class QuotationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ["name", "phone", "email", "product", "service", "quantity",
                  "location", "requirements", "message"]
        widgets = {
            "requirements": forms.Textarea(attrs={"rows": 3}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "location": "Installation location / city",
            "requirements": "Your requirements (capacity, water source, usage...)",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["product"].required = False
        self.fields["service"].required = False
        self.fields["product"].empty_label = "Select a product (optional)"
        self.fields["service"].empty_label = "Select a service (optional)"
        if user is not None and user.is_authenticated and not self.is_bound:
            profile = getattr(user, "profile", None)
            self.fields["name"].initial = user.get_full_name() or user.username
            self.fields["email"].initial = user.email
            if profile:
                self.fields["phone"].initial = profile.phone
                self.fields["location"].initial = profile.city

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("product") and not cleaned.get("service"):
            raise forms.ValidationError(
                "Please select at least a product or a service you need a quote for."
            )
        return cleaned
