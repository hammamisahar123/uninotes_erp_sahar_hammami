from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.decorators import role_required
from inscription.models import ModuleChoisi
from .services import NoteService, CourbeService


@login_required
@role_required('etudiant')
def saisie_notes(request, module_choisi_id):
    mc = get_object_or_404(ModuleChoisi, id=module_choisi_id, inscription__etudiant=request.user)
    note_service = NoteService(mc)

    if request.method == 'POST':
        for level, msg in note_service.sauvegarder_notes(request.POST):
            getattr(messages, level)(request, msg)
        return redirect('notes:saisie_notes', module_choisi_id=mc.id)

    context = {
        'module_choisi': mc,
        'categories': note_service.categories,
        'notes_existantes': note_service.notes_existantes(),
        'moyenne_module': note_service.moyenne_module(),
        'est_modification': note_service.est_modification(),
    }
    return render(request, 'notes/saisie_notes.html', context)


@login_required
def courbe(request):
    etudiant_id = request.GET.get('etudiant_id')
    if request.user.profile.role == 'tuteur' and etudiant_id:
        etudiant = get_object_or_404(User, id=etudiant_id, profile__tuteur=request.user.profile)
    elif request.user.profile.role == 'etudiant':
        etudiant = request.user
    else:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    service = CourbeService(etudiant)
    return render(request, 'notes/courbe.html', service.get_data())
