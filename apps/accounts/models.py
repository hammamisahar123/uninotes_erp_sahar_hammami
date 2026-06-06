from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('tuteur', 'Tuteur'),
    ]

    # Relation 1-1 avec l'utilisateur Django.
    # CASCADE : suppression du profil si l'utilisateur est supprimé.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # max_length=20 pour anticiper l'ajout de rôles plus longs sans migration.
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='etudiant'
    )

    # Auto-référence : un étudiant peut pointer vers un tuteur.
    # SET_NULL : si le tuteur est supprimé, l'étudiant n'est pas affecté.
    # limit_choices_to : filtre l'affichage admin (non contraignant par code).
    tuteur = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etudiants',
        limit_choices_to={'role': 'tuteur'}
    )

    class Meta:
        # Index sur role pour accélérer les filtres fréquents
        # comme Profile.objects.filter(role='etudiant')
        indexes = [
            models.Index(fields=['role']),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        # Contrainte métier : seul un profil avec le rôle 'tuteur'
        # peut être assigné comme tuteur d'un étudiant.
        # limit_choices_to ne protège que l'admin, pas le code.
        if self.tuteur and self.tuteur.role != 'tuteur':
            raise ValidationError(
                "Le tuteur assigné doit avoir le rôle 'tuteur'."
            )
        # Un tuteur ne peut pas être son propre tuteur
        if self.tuteur and self.tuteur == self:
            raise ValidationError(
                "Un profil ne peut pas être son propre tuteur."
            )

    def __str__(self):
        # get_role_display() retourne le label lisible ('Étudiant')
        # plutôt que la valeur brute ('etudiant')
        return f"{self.user.username} ({self.get_role_display()})"