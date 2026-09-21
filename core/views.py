"""Public pages: home, about, contact, static-ish helpers and error handlers."""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from products.models import Category, Product
from services.models import AMCPlan, Service

from .forms import ContactForm
from .models import FAQ, Statistic, Testimonial


def home(request):
    """Homepage - everything shown here comes from the database."""
    context = {
        "page_title": "AquaCare | Water Purifier Manufacturing, Sales & Service",
        "meta_description": (
            "AquaCare manufactures, sells, installs and maintains RO, UV and UF water "
            "purification systems for homes, offices and industries."
        ),
        "categories": Category.objects.filter(is_active=True)[:8],
        "featured_products": Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related("category")[:8],
        "services": Service.objects.filter(is_active=True)[:6],
        "amc_plans": AMCPlan.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_active=True)[:6],
        "faqs": FAQ.objects.filter(is_active=True)[:6],
        "stats": Statistic.objects.filter(is_active=True),
    }
    return render(request, "home.html", context)


def about(request):
    context = {
        "page_title": "About AquaCare | Our Story, Mission & Quality Promise",
        "meta_description": (
            "Learn about AquaCare - our story, mission, manufacturing capability, "
            "quality assurance and the technology behind our water purifiers."
        ),
        "stats": Statistic.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_active=True)[:3],
    }
    return render(request, "about.html", context)


def contact(request):
    """Contact page - submissions are stored in the database."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Thank you! Your message has been received. We'll reply soon."
            )
            return redirect("core:contact")
        messages.error(request, "Please correct the errors highlighted below.")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
                "phone": getattr(request.user.profile, "phone", ""),
            }
        form = ContactForm(initial=initial)

    context = {
        "form": form,
        "page_title": "Contact AquaCare | Sales & Service Support",
        "meta_description": "Call, email or message AquaCare for purifier sales, "
        "installation, repairs and AMC support.",
        "faqs": FAQ.objects.filter(is_active=True)[:5],
    }
    return render(request, "contact.html", context)


def faq_page(request):
    return render(
        request,
        "faq.html",
        {
            "faqs": FAQ.objects.filter(is_active=True),
            "page_title": "Frequently Asked Questions | AquaCare",
            "meta_description": "Answers to common questions about AquaCare water "
            "purifiers, installation, servicing and AMC plans.",
        },
    )


def robots_txt(request):
    """Simple robots.txt pointing crawlers at the sitemap."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /cart/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# ---------------------------------------------------------------------------
# Custom error handlers (wired in config/urls.py)
# ---------------------------------------------------------------------------
def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)
