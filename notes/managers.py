from django.db import models
from django.db.models import Sum, F, Value, FloatField, OuterRef, Subquery
from django.db.models.functions import Coalesce, Cast


class NoteQuerySet(models.QuerySet):
    def with_produit(self):
        return self.annotate(
            produit=Cast('valeur', FloatField()) * Cast('categorie_evaluation__poids', FloatField())
        )

    def total_pondere(self):
        return self.with_produit().aggregate(
            total=Coalesce(Sum('produit'), Value(0.0, output_field=FloatField()))
        )['total']

    def moyenne_module(self, nb_categories):
        total = self.total_pondere()
        complet = self.count() == nb_categories and nb_categories > 0
        return (total / 100.0) if complet else None

    def en_dict_par_categorie(self):
        return {n['categorie_evaluation_id']: float(n['valeur'])
                for n in self.values('categorie_evaluation_id', 'valeur')}
