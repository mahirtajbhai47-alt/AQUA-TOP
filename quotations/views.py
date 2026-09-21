"""Quotation request views."""

from django.contrib import messages
from django.shortcuts import redirect, render

from products.models import Product

from .forms import QuotationForm


def request_quote(request):
    initial = {}
    product_slug = request.GET.get("product")
    if product_slug:
        product = Product.objects.filter(slug=product_slug, is_active=True).first()
        if product:
            initial["product"] = product.pk

    if request.method == "POST":
        form = QuotationForm(request.POST, user=request.user)
        if form.is_valid():
            quotation = form.save(commit=False)
            if request.user.is_authenticated:
                quotation.customer = request.user
            quotation.save()
            messages.success(
                request,
                f"Thanks! Your quotation request {quotation.reference} has been "
                "received. Our sales team will contact you within one business day.",
            )
            return redirect("quotations:quote_success")
        messages.error(request, "Please correct the errors below.")
    else:
        form = QuotationForm(initial=initial, user=request.user)

    return render(
        request,
        "quotations/request_quote.html",
        {
            "form": form,
            "page_title": "Get a Quote | AquaCare Water Purifiers",
            "meta_description": "Request a free, no-obligation quotation for AquaCare "
            "domestic, commercial or industrial water purification systems.",
        },
    )


def quote_success(request):
    return render(
        request,
        "quotations/quote_success.html",
        {"page_title": "Quotation Request Received | AquaCare"},
    )
