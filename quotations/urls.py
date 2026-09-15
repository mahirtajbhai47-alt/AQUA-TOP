from django.urls import path

from . import views

app_name = "quotations"

urlpatterns = [
    path("", views.request_quote, name="request_quote"),
    path("success/", views.quote_success, name="quote_success"),
]
