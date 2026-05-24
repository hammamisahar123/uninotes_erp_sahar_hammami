from django.contrib import admin, messages
from django.db.models import ProtectedError
from .models import CatalogueModule, CategorieEvaluation


class CategorieEvaluationInline(admin.TabularInline):
    model = CategorieEvaluation
    extra = 1
    verbose_name = "Catégorie d'évaluation"
    verbose_name_plural = "Catégories d'évaluation"


@admin.register(CatalogueModule)
class CatalogueModuleAdmin(admin.ModelAdmin):
    list_display = ['intitule', 'coefficient', 'nb_categories', 'est_actif']
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

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            nb_categories=models.Count('categories_evaluation')
        )

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


@admin.register(CategorieEvaluation)
class CategorieEvaluationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'poids', 'module_intitule']
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
