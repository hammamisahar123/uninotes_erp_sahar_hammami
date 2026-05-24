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

    def en_dict_par_categorie(self):
        return {n['categorie_evaluation_id']: float(n['valeur'])
                for n in self.values('categorie_evaluation_id', 'valeur')}
