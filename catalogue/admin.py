from django.contrib import admin
from .models import CatalogueModule, CategorieEvaluation


class CategorieEvaluationInline(admin.TabularInline):
    model = CategorieEvaluation
    extra = 1


@admin.register(CatalogueModule)
class CatalogueModuleAdmin(admin.ModelAdmin):
    list_display = ['intitule', 'coefficient', 'est_actif']
    list_filter = ['est_actif']
    search_fields = ['intitule']
    inlines = [CategorieEvaluationInline]


@admin.register(CategorieEvaluation)
class CategorieEvaluationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'poids', 'module']
    list_filter = ['module']
