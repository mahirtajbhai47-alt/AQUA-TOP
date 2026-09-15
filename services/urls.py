from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("", views.service_list, name="service_list"),
    path("amc/", views.amc_plans, name="amc_plans"),
    path("amc/subscribe/", views.amc_subscribe, name="amc_subscribe"),
    path("amc/subscribe/<slug:slug>/", views.amc_subscribe, name="amc_subscribe_plan"),
    path("book/installation/", views.book_installation, name="book_installation"),
    path("book/repair/", views.book_repair, name="book_repair"),
    path("book/maintenance/", views.book_maintenance, name="book_maintenance"),
    path("track/", views.track_service, name="track"),
    path("technician/", views.technician_dashboard, name="technician_dashboard"),
    path("technician/job/<int:pk>/update/", views.technician_update_status,
         name="technician_update_status"),
    path("<slug:slug>/", views.service_detail, name="service_detail"),
]
