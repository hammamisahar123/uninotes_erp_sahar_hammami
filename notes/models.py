from django.db import models
from inscription.models import ModuleChoisi
from catalogue.models import CategorieEvaluation
from .managers import NoteQuerySet


class Note(models.Model):
    """
    Entité Utilisateur : note saisie par un étudiant pour une catégorie d'évaluation.
    Relation : N -- 1 ModuleChoisi
              N -- 1 CategorieEvaluation
    """
    # La note est liée au module choisi par l'étudiant
    module_choisi = models.ForeignKey(
        ModuleChoisi, on_delete=models.CASCADE,
        related_name='notes', verbose_name="Module choisi"
    )
    # La note est liée à une catégorie d'évaluation du référentiel
    categorie_evaluation = models.ForeignKey(
        CategorieEvaluation, on_delete=models.CASCADE,
        related_name='notes', verbose_name="Catégorie d'évaluation"
    )
    # Valeur de la note entre 0 et 20 inclus
    valeur = models.DecimalField(
        max_digits=4, decimal_places=2,
        verbose_name="Note", help_text="Note entre 0 et 20"
    )
    # Date de saisie pour la reconstitution historique (courbe d'évolution)
    date_saisie = models.DateTimeField(auto_now_add=True, verbose_name="Date de saisie")

    objects = NoteQuerySet.as_manager()

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        # Une seule note par couple (module_choisi, categorie_evaluation)
        unique_together = ['module_choisi', 'categorie_evaluation']
        ordering = ['date_saisie']

    def __str__(self):
        return f"{self.module_choisi} - {self.categorie_evaluation.nom}: {self.valeur}"
