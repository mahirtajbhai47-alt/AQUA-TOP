from django import forms

from core.forms import BootstrapFormMixin

from .models import Order


class CheckoutForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "phone", "email", "address", "city", "state",
                  "pincode", "payment_method", "notes"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {"notes": "Delivery / installation notes (optional)"}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only Cash on Delivery is available in this version; online payment is
        # kept in the model so a gateway (e.g. Razorpay) can be plugged in later.
        self.fields["payment_method"].choices = [
            (Order.PAYMENT_COD, "Cash on Delivery / Pay on Service")
        ]
        if user is not None and user.is_authenticated and not self.is_bound:
            profile = getattr(user, "profile", None)
            self.fields["full_name"].initial = user.get_full_name() or user.username
            self.fields["email"].initial = user.email
            if profile:
                self.fields["phone"].initial = profile.phone
                self.fields["address"].initial = profile.address
                self.fields["city"].initial = profile.city
                self.fields["state"].initial = profile.state
                self.fields["pincode"].initial = profile.pincode
