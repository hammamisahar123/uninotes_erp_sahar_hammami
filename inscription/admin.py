from django.contrib import admin
from .models import Inscription, ModuleChoisi


class ModuleChoisiInline(admin.TabularInline):
    model = ModuleChoisi
    extra = 0


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'annee_academique', 'statut', 'date_creation']
    list_filter = ['statut', 'annee_academique']
    inlines = [ModuleChoisiInline]


@admin.register(ModuleChoisi)
class ModuleChoisiAdmin(admin.ModelAdmin):
    list_display = ['inscription', 'module_catalogue']
