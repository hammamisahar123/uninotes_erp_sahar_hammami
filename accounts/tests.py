from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from accounts.models import Profile

def _make_user(username='test_user', password='testpass123'):
    return User.objects.create_user(username=username, password=password)

def _make_tuteur(username='tuteur_user', password='testpass123'):
    user = User.objects.create_user(username=username, password=password)
    user.profile.role = 'tuteur'
    user.profile.save()
    return user

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.tuteur = _make_tuteur()

    def test_profile_cree_automatiquement(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'etudiant')

    def test_role_tuteur(self):
        self.assertEqual(self.tuteur.profile.role, 'tuteur')

    def test_tuteur_peut_avoir_plusieurs_etudiants(self):
        etu1 = _make_user(username='etu1')
        etu2 = _make_user(username='etu2')
        etu1.profile.tuteur = self.tuteur.profile
        etu1.profile.save()
        etu2.profile.tuteur = self.tuteur.profile
        etu2.profile.save()
        self.assertEqual(self.tuteur.profile.etudiants.count(), 2)

    def test_profile_str(self):
        self.assertIn(self.user.username, str(self.user.profile))
