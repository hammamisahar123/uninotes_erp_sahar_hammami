from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'module', 'categorie_evaluation', 'valeur', 'date_saisie']
    list_filter = ['date_saisie', 'categorie_evaluation__module']
    search_fields = ['module_choisi__inscription__etudiant__username',
                     'categorie_evaluation__module__intitule']
    date_hierarchy = 'date_saisie'
    list_per_page = 25

    fieldsets = [
        ('Module choisi', {'fields': ['module_choisi']}),
        ('Note', {
            'fields': ['categorie_evaluation', 'valeur'],
            'description': 'Note entre 0 et 20, deux décimales max',
        }),
    ]

    def etudiant(self, obj):
        return obj.module_choisi.inscription.etudiant.username
    etudiant.short_description = "Étudiant"
    etudiant.admin_order_field = 'module_choisi__inscription__etudiant__username'

    def module(self, obj):
        return obj.categorie_evaluation.module.intitule
    module.short_description = "Module"
    module.admin_order_field = 'categorie_evaluation__module__intitule'
