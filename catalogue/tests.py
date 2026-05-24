from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from catalogue.models import CatalogueModule, CategorieEvaluation


def _make_module(**kwargs):
    defaults = {'intitule': 'Module', 'coefficient': 10}
    defaults.update(kwargs)
    return CatalogueModule.objects.create(**defaults)

def _make_categorie(nom='CC', poids=40, module=None):
    return CategorieEvaluation.objects.create(nom=nom, poids=poids, module=module)


class CatalogueModuleTest(TestCase):
    def setUp(self):
        self.module = _make_module(intitule='Mathématiques', coefficient=10)

    def test_creation_module(self):
        self.assertEqual(self.module.intitule, 'Mathématiques')
        self.assertEqual(self.module.coefficient, 10)
        self.assertTrue(self.module.est_actif)

    def test_intitule_unique(self):
        with self.assertRaises(IntegrityError):
            _make_module(intitule='Mathématiques')

    def test_inactif_par_defaut(self):
        module = _make_module(est_actif=False)
        self.assertFalse(module.est_actif)


class CategorieEvaluationTest(TestCase):
    def setUp(self):
        self.module = _make_module(intitule='Physique', coefficient=8)
        self.cat = _make_categorie(nom='CC', poids=40, module=self.module)

    def test_nom_module_unique_together(self):
        with self.assertRaises((IntegrityError, ValidationError)):
            _make_categorie(nom='CC', module=self.module)

    def test_deux_modules_meme_nom_categorie_ok(self):
        m2 = _make_module(intitule='Chimie')
        cat2 = _make_categorie(nom='CC', module=m2)
        self.assertIsNotNone(cat2.pk)

    def test_poids_depasse_100(self):
        with self.assertRaises(ValidationError):
            _make_categorie(nom='TP', poids=70, module=self.module)

    def test_poids_negatif(self):
        with self.assertRaises(ValidationError):
            _make_categorie(nom='TP', poids=-10, module=self.module)

    def test_poids_sup_100(self):
        with self.assertRaises(ValidationError):
            _make_categorie(nom='EXAM', poids=150, module=self.module)
