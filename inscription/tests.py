from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from catalogue.models import CatalogueModule, CategorieEvaluation
from inscription.models import Inscription, ModuleChoisi
from inscription.services import PanierService


def _make_etudiant(username='etu', password='testpass123'):
    user = User.objects.create_user(username=username, password=password)
    user.profile.role = 'etudiant'
    user.profile.save()
    return user

def _make_module(**kwargs):
    defaults = {'intitule': 'Module', 'coefficient': 10}
    defaults.update(kwargs)
    return CatalogueModule.objects.create(**defaults)

def _make_categorie(nom='CC', poids=40, module=None):
    return CategorieEvaluation.objects.create(nom=nom, poids=poids, module=module)

def _make_inscription(etudiant=None, annee='2025/2026', statut='ouverte'):
    if etudiant is None:
        etudiant = _make_etudiant(username='inscrit')
    return Inscription.objects.create(etudiant=etudiant, annee_academique=annee, statut=statut)


class PanierServiceTest(TestCase):
    def setUp(self):
        self.user = _make_etudiant()
        self.module1 = _make_module(intitule='Maths', coefficient=20)
        self.module2 = _make_module(intitule='Physique', coefficient=15)
        self.module3 = _make_module(intitule='Chimie', coefficient=10)
        self.module4 = _make_module(intitule='SVT', coefficient=25)

    def test_panier_vide_initial(self):
        service = PanierService(self.user)
        self.assertEqual(service.total_coefficient(), 0)
        self.assertEqual(service.points_restants(), 60)

    def test_ajouter_module(self):
        service = PanierService(self.user)
        success, _ = service.ajouter_module(self.module1.id)
        self.assertTrue(success)
        self.assertEqual(service.total_coefficient(), 20)

    def test_ajouter_module_duplicate(self):
        service = PanierService(self.user)
        service.ajouter_module(self.module1.id)
        success, msg = service.ajouter_module(self.module1.id)
        self.assertFalse(success)

    def test_ajouter_module_depassement(self):
        service = PanierService(self.user)
        service.ajouter_module(self.module4.id)  # 25
        service.ajouter_module(self.module3.id)  # 10 → 35
        service.ajouter_module(self.module1.id)  # +20 → 55
        ModuleChoisi.objects.filter(inscription=service.inscription).delete()
        service.ajouter_module(self.module4.id)  # 25
        service.ajouter_module(self.module2.id)  # +15 → 40
        service.ajouter_module(self.module1.id)  # +20 → 60
        service.inscription.statut = 'ouverte'
        service.inscription.save()
        success, msg = service.ajouter_module(self.module3.id)  # +10 → 70
        self.assertFalse(success)
        self.assertIn('dépasse', msg.lower())

    def test_verrouillage_auto_a_60(self):
        service = PanierService(self.user)
        service.ajouter_module(self.module1.id)  # 20
        service.ajouter_module(self.module2.id)  # 15
        service.ajouter_module(self.module4.id)  # 25
        self.assertEqual(service.total_coefficient(), 60)
        self.assertTrue(service.est_verrouille())

    def test_retirer_module(self):
        service = PanierService(self.user)
        service.ajouter_module(self.module1.id)
        mc = ModuleChoisi.objects.get(inscription__etudiant=self.user)
        success, _ = service.retirer_module(mc.id)
        self.assertTrue(success)
        self.assertEqual(service.total_coefficient(), 0)

    def test_points_restants(self):
        service = PanierService(self.user)
        self.assertEqual(service.points_restants(), 60)
        service.ajouter_module(self.module3.id)
        self.assertEqual(service.points_restants(), 50)

    def test_inactif_exclu_du_catalogue(self):
        module_inactif = _make_module(intitule='Inactif', coefficient=5, est_actif=False)
        service = PanierService(self.user)
        self.assertNotIn(module_inactif, service.modules_disponibles())

    def test_suggestions(self):
        service = PanierService(self.user)
        service.ajouter_module(self.module1.id)  # 20
        service.ajouter_module(self.module2.id)  # +15 → reste 25
        suggestions = service.suggestions()
        self.assertIn(self.module4, suggestions[:1])


class InscriptionModelTest(TestCase):
    def test_inscription_unique_par_annee(self):
        user = _make_etudiant(username='unique_test')
        _make_inscription(etudiant=user, annee='2025/2026')
        with self.assertRaises(IntegrityError):
            _make_inscription(etudiant=user, annee='2025/2026')


class ModuleChoisiModelTest(TestCase):
    def setUp(self):
        self.user = _make_etudiant(username='module_test')
        self.inscription = _make_inscription(etudiant=self.user)
        self.module = _make_module(intitule='Anglais', coefficient=5)

    def test_module_unique_dans_inscription(self):
        ModuleChoisi.objects.create(
            inscription=self.inscription, module_catalogue=self.module
        )
        with self.assertRaises(IntegrityError):
            ModuleChoisi.objects.create(
                inscription=self.inscription, module_catalogue=self.module
            )

    def test_protect_on_delete_catalogue(self):
        ModuleChoisi.objects.create(
            inscription=self.inscription, module_catalogue=self.module
        )
        with self.assertRaises(IntegrityError):
            self.module.delete()
