
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from doctors.models import Doctor
from .models import Appointment


# ==============================
# BOOK APPOINTMENT
# ==============================

@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        id=doctor_id
    )

    if request.method == "POST":

        appointment_date = request.POST.get(
            "appointment_date"
        )

        appointment_time = request.POST.get(
            "appointment_time"
        )

        reason = request.POST.get(
            "reason"
        )

        # Check date and time

        if not appointment_date or not appointment_time:

            messages.error(
                request,
                "Please select appointment date and time."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.id
            )

        # Save appointment

        Appointment.objects.create(

            patient=request.user,

            doctor=doctor,

            appointment_date=appointment_date,

            appointment_time=appointment_time,

            reason=reason,

            status="Pending"

        )

        messages.success(
            request,
            "Appointment booked successfully!"
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "book_appointment.html",
        {
            "doctor": doctor
        }
    )


# ==============================
# MY APPOINTMENTS
# ==============================

@login_required
def my_appointments(request):

    appointments = Appointment.objects.filter(

        patient=request.user

    ).select_related(

        "doctor",

        "doctor__specialization"

    ).order_by(

        "-appointment_date",

        "-appointment_time"

    )

    return render(

        request,

        "my_appointments.html",

        {
            "appointments": appointments
        }

    )
