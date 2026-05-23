from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['module_choisi', 'categorie_evaluation', 'valeur', 'date_saisie']
    list_filter = ['date_saisie']
