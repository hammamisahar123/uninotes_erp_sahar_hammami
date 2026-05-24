from django.db import models
from django.db.models import (
    Count, Sum, F, Value, FloatField, IntegerField,
    Case, When, OuterRef, Subquery, Q
)
from django.db.models.functions import Coalesce, Cast


class ModuleChoisiQuerySet(models.QuerySet):
    def _nb_categories_subq(self):
        from apps.catalogue.models import CategorieEvaluation
        return Coalesce(Subquery(
            CategorieEvaluation.objects.filter(module=OuterRef('module_catalogue'))
            .values('module').annotate(cnt=Count('id')).values('cnt')[:1],
            output_field=IntegerField()
        ), Value(0, output_field=IntegerField()))

    def _nb_notes_subq(self, note_ids=None):
        from apps.notes.models import Note
        qs = Note.objects.filter(module_choisi=OuterRef('id'))
        if note_ids is not None:
            qs = qs.filter(id__in=note_ids)
        return Coalesce(Subquery(
            qs.values('module_choisi').annotate(cnt=Count('id')).values('cnt')[:1],
            output_field=IntegerField()
        ), Value(0, output_field=IntegerField()))

    def _total_pondere_subq(self, note_ids=None):
        from apps.notes.models import Note
        qs = Note.objects.filter(module_choisi=OuterRef('id'))
        if note_ids is not None:
            qs = qs.filter(id__in=note_ids)
        return Coalesce(Subquery(
            qs.annotate(
                p=Cast('valeur', FloatField()) * Cast('categorie_evaluation__poids', FloatField())
            ).values('module_choisi').annotate(
                total=Sum('p')
            ).values('total')[:1],
            output_field=FloatField()
        ), Value(0.0, output_field=FloatField()))

    def with_moyenne(self):
        return self.annotate(
            nb_categories=self._nb_categories_subq(),
            nb_notes=self._nb_notes_subq(),
            total_pondere=self._total_pondere_subq(),
            moyenne=Case(
                When(
                    Q(nb_notes=F('nb_categories')) & Q(nb_notes__gt=0),
                    then=F('total_pondere') / Value(100.0, output_field=FloatField())
                ),
                default=Value(None, output_field=FloatField()),
                output_field=FloatField()
            )
        )

    def with_selects(self):
        return self.select_related(
            'module_catalogue', 'inscription__etudiant'
        ).prefetch_related(
            'module_catalogue__categories_evaluation'
        )

    def total_coefficient(self):
        return self.aggregate(
            total=Coalesce(Sum('module_catalogue__coefficient'), Value(0))
        )['total']

    def moyenne_generale(self):
        qs = self.with_moyenne()
        data = qs.aggregate(
            somme_ponderee=Coalesce(
                Sum(
                    Case(
                        When(
                            Q(nb_notes=F('nb_categories')) & Q(nb_notes__gt=0),
                            then=F('total_pondere') / Value(100.0) * F('module_catalogue__coefficient')
                        ),
                        default=Value(0.0, output_field=FloatField()),
                        output_field=FloatField()
                    )
                ),
                Value(0.0, output_field=FloatField())
            )
        )
        return data['somme_ponderee'] / 60.0

    def evolution_a_la_date(self, note_ids):
        return self.annotate(
            total_pondere=self._total_pondere_subq(note_ids),
            nb_categories=self._nb_categories_subq(),
            nb_notes=self._nb_notes_subq(note_ids),
        ).filter(
            Q(nb_notes__gt=0) & Q(nb_notes=F('nb_categories'))
        )

    def moyenne_ponderee_a_la_date(self, note_ids):
        modules = self.evolution_a_la_date(note_ids)
        data = modules.aggregate(
            total=Coalesce(
                Sum(
                    F('total_pondere') / Value(100.0) * F('module_catalogue__coefficient'),
                    output_field=FloatField()
                ),
                Value(0.0, output_field=FloatField())
            )
        )
        return data['total'] / 60.0 if data['total'] else 0.0
