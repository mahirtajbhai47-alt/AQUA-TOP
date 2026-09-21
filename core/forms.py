from django import forms

from .models import ContactMessage


class BootstrapFormMixin:
    """Adds Bootstrap classes to every widget - keeps templates clean."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
            if not widget.attrs.get("placeholder") and not isinstance(
                widget, (forms.Select, forms.CheckboxInput, forms.ClearableFileInput)
            ):
                widget.attrs["placeholder"] = field.label


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 8:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone
