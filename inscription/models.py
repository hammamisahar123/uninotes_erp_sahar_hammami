from django.db import models
from django.contrib.auth.models import User
from catalogue.models import CatalogueModule


class Inscription(models.Model):
    """
    Entité Utilisateur : inscription d'un étudiant pour une année académique.
    Relation : N -- 1 User (étudiant)
              1 -- N ModuleChoisi
    """
    STATUT_CHOICES = [
        ('ouverte', 'Ouverte'),
        ('verrouillee', 'Verrouillée'),
    ]

    # Un étudiant a une inscription par année académique
    etudiant = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='inscriptions', verbose_name="Étudiant",
        limit_choices_to={'profile__role': 'etudiant'}
    )
    annee_academique = models.CharField(max_length=20, verbose_name="Année académique")
    statut = models.CharField(
        max_length=12, choices=STATUT_CHOICES,
        default='ouverte', verbose_name="Statut"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        # Un étudiant ne peut avoir qu'une inscription par année
        unique_together = ['etudiant', 'annee_academique']

    def __str__(self):
        return f"{self.etudiant.username} - {self.annee_academique} ({self.statut})"


class ModuleChoisi(models.Model):
    """
    Entité Utilisateur : sélection d'un module du catalogue par un étudiant.
    Relation : N -- 1 Inscription
              N -- 1 CatalogueModule
              1 -- N Note
    """
    # Un module choisi appartient à une inscription
    inscription = models.ForeignKey(
        Inscription, on_delete=models.CASCADE,
        related_name='modules_choisis', verbose_name="Inscription"
    )
    # Référence vers le catalogue (séparation Référentiel / Choix)
    module_catalogue = models.ForeignKey(
        CatalogueModule, on_delete=models.CASCADE,
        related_name='choix_etudiants', verbose_name="Module du catalogue"
    )

    class Meta:
        verbose_name = "Module choisi"
        verbose_name_plural = "Modules choisis"
        # Un même module ne peut pas être choisi deux fois dans la même inscription
        unique_together = ['inscription', 'module_catalogue']

    def __str__(self):
        return f"{self.inscription.etudiant.username} -> {self.module_catalogue.intitule}"
