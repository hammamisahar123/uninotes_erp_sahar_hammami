from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required
from .services import PanierService


@login_required
@role_required('etudiant')
def panier(request):
    panier_service = PanierService(request.user)
    context = {
        'inscription': panier_service.inscription,
        'modules_choisis': panier_service.modules_choisis(),
        'total_coeff': panier_service.total_coefficient(),
        'points_restants': panier_service.points_restants(),
        'modules_disponibles': panier_service.modules_disponibles(),
        'suggestions': panier_service.suggestions(),
        'gauge_offset': panier_service.gauge_offset(),
    }
    return render(request, 'inscription/panier.html', context)


@login_required
@role_required('etudiant')
def ajouter_module(request, module_id):
    service = PanierService(request.user)
    success, msg = service.ajouter_module(module_id)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect('inscription:panier')


@login_required
@role_required('etudiant')
def retirer_module(request, module_choisi_id):
    service = PanierService(request.user)
    success, msg = service.retirer_module(module_choisi_id)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect('inscription:panier')
