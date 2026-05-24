"""
URL configuration for uninotes_erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from accounts.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.home, name='home'),
    path('signup/', accounts_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=LoginForm, redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', accounts_views.dashboard, name='dashboard'),
    path('dashboard/tuteur/<int:etudiant_id>/', accounts_views.dashboard_tuteur, name='dashboard_tuteur'),
    path('panier/', include('inscription.urls')),
    path('notes/', include('notes.urls')),
    path('catalogue/', include('catalogue.urls')),
]
