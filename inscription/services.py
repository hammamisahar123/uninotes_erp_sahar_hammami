import math
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from inscription.models import Inscription, ModuleChoisi
from catalogue.models import CatalogueModule


class PanierService:
    """Service métier pour la gestion du panier d'inscription."""

    def __init__(self, user):
        self.user = user
        self.inscription, self._created = Inscription.objects.get_or_create(
            etudiant=user, annee_academique="2025/2026",
            defaults={'statut': 'ouverte'}
        )

    def est_verrouille(self):
        return self.inscription.statut == 'verrouillee'

    def modules_choisis(self):
        return ModuleChoisi.objects.filter(inscription=self.inscription).with_selects()

    def total_coefficient(self):
        return self.modules_choisis().total_coefficient()

    def points_restants(self):
        return 60 - self.total_coefficient()

    def modules_disponibles(self):
        modules_ids = self.modules_choisis().values_list('module_catalogue_id', flat=True)
        return CatalogueModule.objects.filter(est_actif=True).exclude(id__in=modules_ids)

    def suggestions(self):
        points_restants = self.points_restants()
        disponibles = self.modules_disponibles()
        suggestions_exact = disponibles.filter(coefficient=points_restants)
        suggestions_possibles = disponibles.filter(
            coefficient__lte=points_restants
        ).exclude(id__in=suggestions_exact.values_list('id', flat=True)).order_by('-coefficient')
        return list(suggestions_exact) + list(suggestions_possibles)

    def gauge_offset(self):
        total = self.total_coefficient()
        circumference = 2 * math.pi * 54
        return circumference * (1 - total / 60.0) if total > 0 else circumference

    def ajouter_module(self, module_id):
        if self.est_verrouille():
            return False, "Votre inscription est verrouillée. Aucune modification n'est possible."

        module = CatalogueModule.objects.get(id=module_id, est_actif=True)

        if ModuleChoisi.objects.filter(inscription=self.inscription, module_catalogue=module).exists():
            return False, "Ce module est déjà dans votre panier."

        total_actuel = self.total_coefficient()
        nouveau_total = total_actuel + module.coefficient
        if nouveau_total > 60:
            return False, (
                f"Impossible d'ajouter le module {module.intitule} "
                f"(coefficient : {module.coefficient}). "
                f"Votre total actuel est de {total_actuel} points. "
                f"L'ajout porterait le total à {nouveau_total} points, "
                f"ce qui dépasse la limite de 60."
            )

        ModuleChoisi.objects.create(inscription=self.inscription, module_catalogue=module)

        if nouveau_total == 60:
            self.inscription.statut = 'verrouillee'
            self.inscription.save()
            return True, "Votre inscription est verrouillée. Vous ne pouvez plus modifier votre sélection de modules."

        return True, f"{module.intitule} ajouté au panier."

    def retirer_module(self, module_choisi_id):
        mc = ModuleChoisi.objects.get(id=module_choisi_id, inscription__etudiant=self.user)
        if mc.inscription.statut != 'ouverte':
            return False, "Votre inscription est verrouillée. Aucune modification n'est possible."
        mc.delete()
        return True, "Module retiré du panier."
