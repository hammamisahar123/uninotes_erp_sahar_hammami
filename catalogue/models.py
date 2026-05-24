from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum


class CatalogueModule(models.Model):
    """
    Entité du Référentiel : module proposé par l'établissement.
    Relation : 1 -- N CategorieEvaluation
              N -- M ModuleChoisi (via inscription)
    """
    intitule = models.CharField(max_length=200, unique=True, verbose_name="Intitulé")
    coefficient = models.PositiveIntegerField(verbose_name="Coefficient")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Module du catalogue"
        verbose_name_plural = "Modules du catalogue"
        ordering = ['intitule']

    def __str__(self):
        return f"{self.intitule} (coeff. {self.coefficient})"


class CategorieEvaluation(models.Model):
    """
    Entité du Référentiel : catégorie d'évaluation d'un module.
    Relation : N -- 1 CatalogueModule
              1 -- N Note
    """
    nom = models.CharField(max_length=100, verbose_name="Nom")
    poids = models.PositiveIntegerField(verbose_name="Poids (%)")
    module = models.ForeignKey(
        CatalogueModule, on_delete=models.CASCADE,
        related_name='categories_evaluation', verbose_name="Module"
    )

    class Meta:
        verbose_name = "Catégorie d'évaluation"
        verbose_name_plural = "Catégories d'évaluation"
        unique_together = ['nom', 'module']
        ordering = ['module', 'nom']

    def clean(self):
        if self.poids <= 0:
            raise ValidationError({'poids': "Le poids doit être supérieur à 0."})
        if self.poids > 100:
            raise ValidationError({'poids': "Le poids ne peut pas dépasser 100%."})
        autres = CategorieEvaluation.objects.filter(module=self.module)
        if self.pk:
            autres = autres.exclude(pk=self.pk)
        total_autres = autres.aggregate(s=Sum('poids'))['s'] or 0
        if total_autres + self.poids > 100:
            raise ValidationError(
                f"La somme des poids du module « {self.module.intitule} » "
                f"dépasserait 100% (actuel : {total_autres}% + {self.poids}% = {total_autres + self.poids}%)."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.poids}%) - {self.module.intitule}"
