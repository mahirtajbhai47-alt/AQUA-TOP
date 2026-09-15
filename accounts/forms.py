from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from core.forms import BootstrapFormMixin

from .models import CustomerProfile


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Registration form - saves the user AND the customer profile."""

    first_name = forms.CharField(max_length=60, label="First name")
    last_name = forms.CharField(max_length=60, required=False, label="Last name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=20, label="Phone number")
    city = forms.CharField(max_length=80, required=False, label="City")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "phone", "city"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data["email"]
        user.save()  # profile is created by the post_save signal
        profile = user.profile
        profile.phone = self.cleaned_data["phone"]
        profile.city = self.cleaned_data.get("city", "")
        profile.save()
        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label="Username or email")


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["phone", "address", "city", "state", "pincode", "avatar"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}
