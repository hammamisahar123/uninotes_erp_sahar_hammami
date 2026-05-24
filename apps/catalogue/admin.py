from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ProtectedError
from django.utils.html import format_html
from .models import CatalogueModule, CategorieEvaluation


class CategorieEvaluationInlineForm(forms.ModelForm):
    class Meta:
        model = CategorieEvaluation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        poids = cleaned_data.get('poids')
        module = cleaned_data.get('module')
        if poids and module:
            if poids <= 0:
                raise ValidationError({'poids': "Le poids doit être supérieur à 0."})
            if poids > 100:
                raise ValidationError({'poids': "Le poids ne peut pas dépasser 100%."})
        return cleaned_data


class CategorieEvaluationInline(admin.TabularInline):
    model = CategorieEvaluation
    form = CategorieEvaluationInlineForm
    extra = 1
    verbose_name = "Catégorie d'évaluation"
    verbose_name_plural = "Catégories d'évaluation"

    def clean(self, formset):
        total = sum(
            form.cleaned_data.get('poids', 0) or 0
            for form in formset.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        )
        if formset.forms and total != 100:
            raise ValidationError(
                f"La somme des poids doit être égale à 100% (actuellement : {total}%)."
            )


class CatalogueModuleAdminForm(forms.ModelForm):
    class Meta:
        model = CatalogueModule
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


@admin.register(CatalogueModule)
class CatalogueModuleAdmin(admin.ModelAdmin):
    form = CatalogueModuleAdminForm
    list_display = ['intitule', 'coefficient', 'nb_categories', 'est_actif', 'poids_total']
    list_filter = ['est_actif', 'coefficient']
    search_fields = ['intitule', 'description']
    list_editable = ['est_actif']
    list_per_page = 25
    inlines = [CategorieEvaluationInline]

    fieldsets = [
        ('Informations générales', {
            'fields': ['intitule', 'coefficient', 'description'],
        }),
        ('État', {
            'fields': ['est_actif'],
            'description': 'Décocher pour archiver le module (masqué du catalogue, '
                           'données existantes préservées)',
        }),
    ]

    def nb_categories(self, obj):
        return obj.categories_evaluation.count()
    nb_categories.short_description = "Catégories"
    nb_categories.admin_order_field = 'nb_categories'

    def poids_total(self, obj):
        total = obj.categories_evaluation.aggregate(
            total=models.Sum('poids')
        )['total'] or 0
        couleur = 'text-emerald-600' if total == 100 else 'text-red-500'
        return format_html(f'<span class="{couleur} font-bold">{total}%</span>')
    poids_total.short_description = "Poids total"
    poids_total.admin_order_field = 'poids_total'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            nb_categories=models.Count('categories_evaluation'),
            poids_total=models.Sum('categories_evaluation__poids')
        )

    class Media:
        js = ('admin/js/poids_validation.js',)

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError:
            nb_choix = obj.choix_etudiants.count()
            self.message_user(
                request,
                f"Suppression refusée : le module « {obj.intitule} » est référencé par "
                f"{nb_choix} choix d'étudiant(s). Utilisez l'archivage (décocher 'Actif') "
                f"pour le masquer du catalogue tout en préservant les données.",
                level=messages.ERROR,
            )

    def delete_queryset(self, request, queryset):
        protected = []
        for obj in queryset:
            try:
                obj.delete()
            except ProtectedError:
                nb_choix = obj.choix_etudiants.count()
                protected.append(f"« {obj.intitule} » ({nb_choix} choix)")
        if protected:
            self.message_user(
                request,
                "Suppression refusée pour les modules suivants (référencés par des choix "
                f"d'étudiants) : {'; '.join(protected)}. "
                "Utilisez l'archivage (décocher 'Actif') comme alternative.",
                level=messages.ERROR,
            )


class CategorieEvaluationForm(forms.ModelForm):
    class Meta:
        model = CategorieEvaluation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        poids = cleaned_data.get('poids')
        module = cleaned_data.get('module')
        if poids and module:
            if poids <= 0:
                raise ValidationError({'poids': "Le poids doit être supérieur à 0."})
            if poids > 100:
                raise ValidationError({'poids': "Le poids ne peut pas dépasser 100%."})
            autres = CategorieEvaluation.objects.filter(module=module)
            if self.instance.pk:
                autres = autres.exclude(pk=self.instance.pk)
            total_autres = autres.aggregate(s=models.Sum('poids'))['s'] or 0
            if total_autres + poids > 100:
                raise ValidationError(
                    f"La somme des poids du module dépasserait 100% "
                    f"(actuel : {total_autres}% + {poids}% = {total_autres + poids}%)."
                )
        return cleaned_data


@admin.register(CategorieEvaluation)
class CategorieEvaluationAdmin(admin.ModelAdmin):
    form = CategorieEvaluationForm
    list_display = ['nom', 'poids', 'module_intitule', 'poids_module']
    list_filter = ['module']
    search_fields = ['nom', 'module__intitule']
    list_per_page = 25

    fieldsets = [
        ('Module parent', {'fields': ['module']}),
        ('Évaluation', {
            'fields': ['nom', 'poids'],
            'description': 'Le poids est exprimé en pourcentage. '
                           'La somme des poids de toutes les catégories d\'un module doit être 100%.',
        }),
    ]

    def module_intitule(self, obj):
        return obj.module.intitule
    module_intitule.short_description = "Module"
    module_intitule.admin_order_field = 'module__intitule'

    def poids_module(self, obj):
        total = CategorieEvaluation.objects.filter(module=obj.module).aggregate(
            s=models.Sum('poids')
        )['s'] or 0
        couleur = 'text-emerald-600' if total == 100 else 'text-red-500'
        return format_html(f'<span class="{couleur} font-bold">{total}%</span>')
    poids_module.short_description = "Total module"
