from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .decorators import role_required
from .forms import SignupForm
from .services import DashboardService


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie.")
            return redirect('dashboard')
    return render(request, 'registration/signup.html', {'form': form})


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin:index')
    return render(request, 'accounts/home.html')


@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        return redirect('admin:index')
    if user.profile.role == 'etudiant':
        service = DashboardService(user)
        return render(request, 'accounts/dashboard.html', service.get_context())

    etudiants = User.objects.filter(
        profile__tuteur=user.profile, profile__role='etudiant'
    )
    return render(request, 'accounts/dashboard.html', {'etudiants': etudiants})


@login_required
@role_required('tuteur')
def dashboard_tuteur(request, etudiant_id):
    etudiant = get_object_or_404(
        User, id=etudiant_id, profile__tuteur=request.user.profile
    )
    service = DashboardService(etudiant)
    return render(request, 'accounts/dashboard.html', service.get_context())
