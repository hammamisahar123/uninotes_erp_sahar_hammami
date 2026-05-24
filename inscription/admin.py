from django.db import models
from django.contrib import admin
from .models import Inscription, ModuleChoisi


class ModuleChoisiInline(admin.TabularInline):
    model = ModuleChoisi
    extra = 3
    verbose_name = "Module choisi"
    verbose_name_plural = "Modules choisis"
    fields = ['module_catalogue']
    autocomplete_fields = ['module_catalogue']


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'annee_academique', 'statut', 'total_coefficients', 'date_creation']
    list_filter = ['statut', 'annee_academique']
    search_fields = ['etudiant__username', 'etudiant__email']
    list_per_page = 25
    inlines = [ModuleChoisiInline]
    autocomplete_fields = ['etudiant']

    fieldsets = [
        ('Étudiant', {'fields': ['etudiant']}),
        ('Année académique', {'fields': ['annee_academique']}),
        ('Statut', {
            'fields': ['statut'],
            'description': 'Verrouillée = plus de modifications possibles',
        }),
    ]

    def total_coefficients(self, obj):
        total = obj.modules_choisis.aggregate(
            total=models.Sum('module_catalogue__coefficient')
        )['total'] or 0
        return f"{total} / 60"
    total_coefficients.short_description = "Total coeff."


@admin.register(ModuleChoisi)
class ModuleChoisiAdmin(admin.ModelAdmin):
    list_display = ['etudiant_nom', 'module_catalogue', 'coefficient', 'inscription_statut']
    list_filter = ['inscription__statut', 'module_catalogue']
    search_fields = ['inscription__etudiant__username', 'module_catalogue__intitule']
    list_per_page = 25
    autocomplete_fields = ['inscription', 'module_catalogue']

    fieldsets = [
        ('Inscription', {'fields': ['inscription']}),
        ('Module', {'fields': ['module_catalogue']}),
    ]

    def etudiant_nom(self, obj):
        return obj.inscription.etudiant.username
    etudiant_nom.short_description = "Étudiant"
    etudiant_nom.admin_order_field = 'inscription__etudiant__username'

    def coefficient(self, obj):
        return obj.module_catalogue.coefficient
    coefficient.short_description = "Coeff."

    def inscription_statut(self, obj):
        return obj.inscription.statut
    inscription_statut.short_description = "Statut inscription"
