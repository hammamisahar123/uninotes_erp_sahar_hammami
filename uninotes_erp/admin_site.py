from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import GroupAdmin

from apps.accounts.models import Profile
from apps.accounts.admin import UserAdmin as CustomUserAdmin, ProfileAdmin
from apps.catalogue.models import CatalogueModule, CategorieEvaluation
from apps.catalogue.admin import CatalogueModuleAdmin, CategorieEvaluationAdmin
from apps.inscription.models import Inscription, ModuleChoisi
from apps.inscription.admin import InscriptionAdmin, ModuleChoisiAdmin
from apps.notes.models import Note
from apps.notes.admin import NoteAdmin


class IndependentAdminSite(AdminSite):
    site_header = "UniNotes Administration"
    site_title = "UniNotes Admin"
    index_title = "Administration"


admin_site = IndependentAdminSite(name='admin')

admin_site.register(User, CustomUserAdmin)
admin_site.register(Profile, ProfileAdmin)
admin_site.register(CatalogueModule, CatalogueModuleAdmin)
admin_site.register(CategorieEvaluation, CategorieEvaluationAdmin)
admin_site.register(Inscription, InscriptionAdmin)
admin_site.register(ModuleChoisi, ModuleChoisiAdmin)
admin_site.register(Note, NoteAdmin)
admin_site.register(Group, GroupAdmin)
