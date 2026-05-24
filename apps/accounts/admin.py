from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Profile


class TuteurListFilter(admin.SimpleListFilter):
    title = _('Tuteur')
    parameter_name = 'tuteur'

    def lookups(self, request, model_admin):
        tuteurs = Profile.objects.filter(
            role='tuteur'
        ).select_related('user').order_by('user__username')
        return [(t.id, t.user.username) for t in tuteurs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tuteur__id=self.value())
        return queryset


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tuteur' in self.fields:
            self.fields['tuteur'].queryset = Profile.objects.filter(
                role='tuteur'
            ).select_related('user')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        tuteur = cleaned_data.get('tuteur')
        if role == 'tuteur' and tuteur:
            raise forms.ValidationError(
                "Un tuteur ne peut pas avoir de tuteur. "
                "Le champ Parrainage est réservé aux étudiants."
            )
        return cleaned_data


class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileAdminForm
    can_delete = False
    verbose_name = "Profil"
    verbose_name_plural = "Profils"
    fieldsets = [
        ('Rôle', {'fields': ['role']}),
        ('Parrainage', {
            'fields': ['tuteur'],
            'description': 'Tuteur assigné à cet étudiant (accès lecture seule aux données)',
        }),
    ]

    class Media:
        js = ('admin/js/profile_role.js',)


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'nom_complet', 'email', 'get_role', 'get_tuteur', 'is_staff', 'date_joined']
    list_filter = list(BaseUserAdmin.list_filter) + ['profile__role']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else '-'
    get_role.short_description = "Rôle"
    get_role.admin_order_field = 'profile__role'

    def get_tuteur(self, obj):
        if hasattr(obj, 'profile') and obj.profile.tuteur:
            return obj.profile.tuteur.user.get_full_name() or obj.profile.tuteur.user.username
        return '-'
    get_tuteur.short_description = "Tuteur"

    def nom_complet(self, obj):
        return obj.get_full_name() or obj.username
    nom_complet.short_description = "Nom complet"


class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ['nom_complet', 'role', 'tuteur_nom', 'inscrit_le']
    list_filter = ['role', TuteurListFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    list_per_page = 25

    fieldsets = [
        ('Utilisateur', {'fields': ['user']}),
        ('Rôle', {'fields': ['role']}),
        ('Parrainage', {
            'fields': ['tuteur'],
            'description': 'Sélectionner le tuteur à assigner à cet étudiant',
        }),
    ]

    class Media:
        js = ('admin/js/profile_role.js',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tuteur__user')

    def nom_complet(self, obj):
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username
    nom_complet.short_description = "Nom"
    nom_complet.admin_order_field = 'user__last_name'

    def tuteur_nom(self, obj):
        if obj.tuteur:
            return obj.tuteur.user.get_full_name() or obj.tuteur.user.username
        return "—"
    tuteur_nom.short_description = "Tuteur"
    tuteur_nom.admin_order_field = 'tuteur__user__last_name'

    def inscrit_le(self, obj):
        return obj.user.date_joined
    inscrit_le.short_description = "Inscrit le"
    inscrit_le.admin_order_field = 'user__date_joined'
