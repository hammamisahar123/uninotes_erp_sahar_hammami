from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from catalogue.models import CatalogueModule, CategorieEvaluation
from inscription.models import Inscription, ModuleChoisi
from notes.models import Note


class Command(BaseCommand):
    help = "Peuple la base de données avec des données de test"

    def handle(self, *args, **options):
        self.stdout.write("Création des données de test...")

        # --- TUTEUR ---
        tuteur = User.objects.create_user(
            username="sami.sifi", email="sami.sifi@esprit.tn", password="password123"
        )
        tuteur.profile.role = "tuteur"
        tuteur.profile.save()

        # --- 3 ÉTUDIANTS ---
        etu1 = User.objects.create_user(
            username="ahmed.benali", email="ahmed@esprit.tn", password="password123"
        )
        etu1.profile.role = "etudiant"
        etu1.profile.tuteur = tuteur.profile
        etu1.profile.save()

        etu2 = User.objects.create_user(
            username="sarah.trabelsi", email="sarah@esprit.tn", password="password123"
        )
        etu2.profile.role = "etudiant"
        etu2.profile.tuteur = tuteur.profile
        etu2.profile.save()

        etu3 = User.objects.create_user(
            username="mehdi.khalil", email="mehdi@esprit.tn", password="password123"
        )
        etu3.profile.role = "etudiant"
        etu3.profile.tuteur = tuteur.profile
        etu3.profile.save()

        self.stdout.write("  [OK] Utilisateurs crees")

        # --- 12 MODULES DU CATALOGUE (total coefficients = 60) ---
        modules_data = [
            ("Algorithmique et Problem Solving", 5, ""),
            ("Conception orientée objet et programmation Java", 6, ""),
            ("Data warehousing", 4, ""),
            ("Framework Python pour le web", 6, ""),
            ("Fundamentals on Deep Learning", 4, ""),
            ("Génie logiciel", 6, ""),
            ("Machine Learning basics", 5, ""),
            ("Multimodal AI", 4, ""),
            ("Python pour l'ingénierie des données", 5, ""),
            ("Système de gestion de base de données", 5, ""),
            ("Techniques d'estimation pour l'ingénieur", 5, ""),
            ("Techniques d'optimisation", 5, ""),
        ]
        modules = []
        for intitule, coeff, desc in modules_data:
            mod = CatalogueModule.objects.create(
                intitule=intitule, coefficient=coeff, description=desc
            )
            modules.append(mod)

        self.stdout.write("  [OK] 12 modules du catalogue crees")

        # --- CATÉGORIES D'ÉVALUATION pour chaque module ---
        categories_data = [
            ("CC", 40, "Contrôle Continu"),
            ("EXAM", 60, "Examen Terminal"),
        ]
        for mod in modules:
            for nom, poids, _ in categories_data:
                CategorieEvaluation.objects.create(nom=nom, poids=poids, module=mod)

        self.stdout.write("  [OK] Categories d evaluation creees")

        # --- 3 INSCRIPTIONS ---
        ins1 = Inscription.objects.create(
            etudiant=etu1, annee_academique="2025/2026", statut="verrouillee"
        )
        ins2 = Inscription.objects.create(
            etudiant=etu2, annee_academique="2025/2026", statut="verrouillee"
        )
        ins3 = Inscription.objects.create(
            etudiant=etu3, annee_academique="2025/2026", statut="ouverte"
        )

        self.stdout.write("  [OK] Inscriptions creees")

        # --- MODULES CHOISIS ---
        # etu1: total 60 (8+6+7+6+8+5+4+6+5+5 = 60) - tous les modules
        etu1_modules = modules  # 60 points

        # etu2: 8+7+8+6+6+5+5+6+5+4 = 60 - tous sauf un différent
        etu2_modules = [
            modules[1], modules[4], modules[6], modules[0],
            modules[2], modules[5], modules[7], modules[3],
            modules[9], modules[8],
        ]

        # etu3: seulement 5 modules (inscription ouverte)
        etu3_modules = modules[:5]

        for ins, mods in [(ins1, etu1_modules), (ins2, etu2_modules), (ins3, etu3_modules)]:
            for mod in mods:
                ModuleChoisi.objects.create(inscription=ins, module_catalogue=mod)

        self.stdout.write("  [OK] Modules choisis crees")

        # --- NOTES ---
        # etu1: quelques notes
        cat_cc = CategorieEvaluation.objects.get(nom="CC", module=modules[0])
        cat_exam = CategorieEvaluation.objects.get(nom="EXAM", module=modules[0])
        mc1 = ModuleChoisi.objects.get(
            inscription=ins1, module_catalogue=modules[0]
        )
        Note.objects.create(
            module_choisi=mc1, categorie_evaluation=cat_cc, valeur=15.0
        )
        Note.objects.create(
            module_choisi=mc1, categorie_evaluation=cat_exam, valeur=13.5
        )

        mc2 = ModuleChoisi.objects.get(
            inscription=ins1, module_catalogue=modules[1]
        )
        Note.objects.create(
            module_choisi=mc2,
            categorie_evaluation=CategorieEvaluation.objects.get(nom="CC", module=modules[1]),
            valeur=12.0,
        )
        Note.objects.create(
            module_choisi=mc2,
            categorie_evaluation=CategorieEvaluation.objects.get(nom="EXAM", module=modules[1]),
            valeur=16.0,
        )

        # etu2: une note partielle
        mc3 = ModuleChoisi.objects.get(
            inscription=ins2, module_catalogue=modules[0]
        )
        Note.objects.create(
            module_choisi=mc3,
            categorie_evaluation=CategorieEvaluation.objects.get(nom="CC", module=modules[0]),
            valeur=14.0,
        )

        self.stdout.write("  [OK] Notes creees")
        self.stdout.write(self.style.SUCCESS("Donnees de test creees avec succes !"))
