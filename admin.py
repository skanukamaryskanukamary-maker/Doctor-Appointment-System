from django.contrib import admin
from .models import Doctor, Specialization


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "specialization",
        "experience",
        "consultation_fee",
    )

    list_display_links = ("name",)

    list_filter = ("specialization",)

    search_fields = (
        "name",
        "email",
        "phone",
    )

    fields = (
        "name",
        "email",
        "phone",
        "specialization",
        "qualification",
        "experience",
        "consultation_fee",
        "available_days",
        "available_time",
        "profile_image",
    )