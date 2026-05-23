from django.db import models


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
    # Un module peut avoir plusieurs catégories d'évaluation
    module = models.ForeignKey(
        CatalogueModule, on_delete=models.CASCADE,
        related_name='categories_evaluation', verbose_name="Module"
    )

    class Meta:
        verbose_name = "Catégorie d'évaluation"
        verbose_name_plural = "Catégories d'évaluation"
        unique_together = ['nom', 'module']
        ordering = ['module', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.poids}%) - {self.module.intitule}"
