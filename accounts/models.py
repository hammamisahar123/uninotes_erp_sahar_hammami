from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('tuteur', 'Tuteur'),
    ]

    # Relation 1-1 avec l'utilisateur Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Rôle : étudiant ou tuteur
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='etudiant')
    # Relation 1-N : un tuteur parraine plusieurs étudiants (auto-référence)
    # Un étudiant peut avoir un tuteur, un tuteur peut avoir plusieurs étudiants
    tuteur = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='etudiants', limit_choices_to={'role': 'tuteur'}
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
