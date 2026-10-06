from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

from django.conf import settings
from django.conf.urls.static import static

from accounts.models import PatientProfile
from doctors.models import Doctor, Specialization
from appointments.models import Appointment


# ================= HOME =================

def home(request):
    return render(request, "home.html")


# ================= REGISTER =================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already registered."
            )

            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        PatientProfile.objects.create(
            user=user,
            phone=phone
        )

        messages.success(
            request,
            "Registration successful. You can now login."
        )

        return redirect("login")

    return render(
        request,
        "register.html"
    )


# ================= LOGIN =================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff or user.is_superuser:

                return redirect(
                    "admin_dashboard"
                )

            return redirect(
                "dashboard"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

        return redirect("login")

    return render(
        request,
        "login.html"
    )


# ================= PATIENT DASHBOARD =================

def dashboard(request):

    if not request.user.is_authenticated:

        return redirect("login")

    return render(
        request,
        "dashboard.html"
    )


# ================= DOCTOR LIST =================

def doctor_list(request):

    doctors = Doctor.objects.select_related(
        "specialization"
    ).all()

    specializations = Specialization.objects.all()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    selected_specialization = request.GET.get(
        "specialization",
        ""
    )

    if search:

        doctors = doctors.filter(

            Q(name__icontains=search) |

            Q(
                specialization__name__icontains=search
            ) |

            Q(
                qualification__icontains=search
            )

        )

    if selected_specialization:

        doctors = doctors.filter(
            specialization_id=selected_specialization
        )

    return render(
        request,
        "doctors.html",
        {
            "doctors": doctors,
            "specializations": specializations,
            "search": search,
            "selected_specialization": selected_specialization,
        }
    )


# ================= DOCTOR DETAIL =================

def doctor_detail(request, doctor_id):

    doctor = get_object_or_404(

        Doctor.objects.select_related(
            "specialization"
        ),

        id=doctor_id

    )

    return render(
        request,
        "doctor_detail.html",
        {
            "doctor": doctor
        }
    )


# ================= ADMIN DASHBOARD =================

def admin_dashboard(request):

    if not request.user.is_authenticated:

        return redirect("login")

    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        messages.error(
            request,
            "You do not have permission to access the admin dashboard."
        )

        return redirect("dashboard")

    total_doctors = Doctor.objects.count()

    total_patients = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    total_appointments = Appointment.objects.count()

    pending_appointments = Appointment.objects.filter(
        status="Pending"
    ).count()

    confirmed_appointments = Appointment.objects.filter(
        status="Confirmed"
    ).count()

    rejected_appointments = Appointment.objects.filter(
        status="Rejected"
    ).count()

    cancelled_appointments = Appointment.objects.filter(
        status="Cancelled"
    ).count()

    completed_appointments = Appointment.objects.filter(
        status="Completed"
    ).count()

    recent_appointments = Appointment.objects.select_related(
        "patient",
        "doctor"
    ).order_by(
        "-created_at"
    )[:5]

    context = {

        "total_doctors":
            total_doctors,

        "total_patients":
            total_patients,

        "total_appointments":
            total_appointments,

        "pending_appointments":
            pending_appointments,

        "confirmed_appointments":
            confirmed_appointments,

        "rejected_appointments":
            rejected_appointments,

        "cancelled_appointments":
            cancelled_appointments,

        "completed_appointments":
            completed_appointments,

        "recent_appointments":
            recent_appointments,
    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )


# ================= LOGOUT =================

def user_logout(request):

    logout(request)

    return redirect("home")


# ================= URL PATTERNS =================

urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        home,
        name="home"
    ),

    path(
        "register/",
        register,
        name="register"
    ),

    path(
        "login/",
        user_login,
        name="login"
    ),

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    path(
        "admin-dashboard/",
        admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "doctors/",
        doctor_list,
        name="doctor_list"
    ),

    path(
        "doctors/<int:doctor_id>/",
        doctor_detail,
        name="doctor_detail"
    ),

    path(
        "logout/",
        user_logout,
        name="logout"
    ),

    path(
        "appointments/",
        include("appointments.urls")
    ),
]


# ================= MEDIA FILES =================

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)