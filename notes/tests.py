from django.test import TestCase
from django.db import IntegrityError
from decimal import Decimal
from django.contrib.auth.models import User
from catalogue.models import CatalogueModule, CategorieEvaluation
from inscription.models import Inscription, ModuleChoisi
from notes.models import Note
from notes.services import NoteService


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

def _make_module_choisi(module_catalogue=None, etudiant=None):
    if module_catalogue is None:
        module_catalogue = _make_module()
    inscription = _make_inscription(etudiant=etudiant)
    return ModuleChoisi.objects.create(inscription=inscription, module_catalogue=module_catalogue)


class NoteServiceTest(TestCase):
    def setUp(self):
        self.module = _make_module(intitule='Maths', coefficient=20)
        self.cc = _make_categorie(nom='CC', poids=40, module=self.module)
        self.examen = _make_categorie(nom='Examen', poids=60, module=self.module)
        self.mc = _make_module_choisi(module_catalogue=self.module)
        self.service = NoteService(self.mc)

    def test_categories_chargees(self):
        self.assertEqual(len(self.service.categories), 2)

    def test_notes_existantes_vide_initial(self):
        self.assertEqual(self.service.notes_existantes(), {})

    def test_sauvegarder_note_valide(self):
        post_data = {f'note_{self.cc.id}': '15.5'}
        self.service.sauvegarder_notes(post_data)
        note = Note.objects.get(module_choisi=self.mc, categorie_evaluation=self.cc)
        self.assertEqual(note.valeur, Decimal('15.50'))

    def test_sauvegarder_note_invalide(self):
        post_data = {f'note_{self.cc.id}': '25'}
        results = self.service.sauvegarder_notes(post_data)
        self.assertTrue(any(level == 'error' for level, _ in results))

    def test_est_complet_vrai_quand_toutes_saisies(self):
        Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.cc, valeur=15)
        Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.examen, valeur=12)
        self.assertTrue(self.service.est_complet())

    def test_moyenne_module_calcul(self):
        Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.cc, valeur=20)
        Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.examen, valeur=10)
        attendue = 20 * 0.40 + 10 * 0.60
        self.assertAlmostEqual(self.service.moyenne_module(), attendue)

    def test_moyenne_module_none_si_incomplet(self):
        Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.cc, valeur=15)
        self.assertIsNone(self.service.moyenne_module())

    def test_update_ecrase_note_existante(self):
        self.service.sauvegarder_notes({f'note_{self.cc.id}': '12'})
        self.service.sauvegarder_notes({f'note_{self.cc.id}': '18'})
        note = Note.objects.get(module_choisi=self.mc, categorie_evaluation=self.cc)
        self.assertEqual(note.valeur, Decimal('18.00'))
        self.assertEqual(Note.objects.count(), 1)


class NoteModelTest(TestCase):
    def setUp(self):
        self.module = _make_module(intitule='Physique', coefficient=15)
        self.cat = _make_categorie(nom='TP', poids=30, module=self.module)
        self.mc = _make_module_choisi(module_catalogue=self.module)

    def test_note_unique_par_module_categorie(self):
        Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.cat, valeur=14)
        with self.assertRaises(IntegrityError):
            Note.objects.create(module_choisi=self.mc, categorie_evaluation=self.cat, valeur=16)
