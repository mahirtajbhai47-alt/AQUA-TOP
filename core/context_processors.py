"""Make company info available in every template."""

from .models import CompanyInfo


def site_context(request):
    return {
        "company": CompanyInfo.get_solo(),
        "site_name": "AquaCare",
    }
