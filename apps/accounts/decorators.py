from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Vérification que le profil existe
            try:
                profile = request.user.profile
            except Exception:
                messages.error(request, "Profil introuvable. Contactez un administrateur.")
                return redirect('home')

            # Vérification du rôle
            if profile.role not in roles:
                messages.error(request, "Accès non autorisé pour votre rôle.")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator