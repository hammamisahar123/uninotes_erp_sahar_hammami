from django.contrib.auth.models import User
from django.db.models import Prefetch
from inscription.models import Inscription, ModuleChoisi
from notes.models import Note


class DashboardService:
    """Service métier pour les données du dashboard étudiant et tuteur."""

    def __init__(self, etudiant):
        self.etudiant = etudiant
        self.inscription = Inscription.objects.filter(etudiant=etudiant).first()

    def modules_choisis(self):
        if not self.inscription:
            return []
        return ModuleChoisi.objects.filter(
            inscription=self.inscription
        ).with_moyenne().with_selects().prefetch_related(
            Prefetch('notes', queryset=Note.objects.select_related('categorie_evaluation'))
        )

    def total_coefficient(self):
        if not self.inscription:
            return 0
        return ModuleChoisi.objects.filter(
            inscription=self.inscription
        ).total_coefficient()

    def moyenne_generale(self):
        if not self.inscription:
            return None
        return ModuleChoisi.objects.filter(
            inscription=self.inscription
        ).moyenne_generale()

    def notes_par_categorie(self):
        if not self.inscription:
            return {}
        module_ids = ModuleChoisi.objects.filter(
            inscription=self.inscription
        ).values_list('id', flat=True)
        notes_qs = Note.objects.filter(module_choisi_id__in=list(module_ids))
        result = {}
        for note in notes_qs:
            mc_id = note.module_choisi_id
            if mc_id not in result:
                result[mc_id] = {}
            result[mc_id][note.categorie_evaluation_id] = note.valeur
        return result

    def get_context(self):
        return {
            'etudiant': self.etudiant,
            'inscription': self.inscription,
            'modules_choisis': self.modules_choisis(),
            'moyenne_generale': self.moyenne_generale(),
            'total_coeff': self.total_coefficient(),
            'notes_par_categorie': self.notes_par_categorie(),
        }



