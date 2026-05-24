from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.catalogue.models import CatalogueModule, CategorieEvaluation


def _annee_courante():
    today = date.today()
    if today.month >= 9:
        return f"{today.year}/{today.year + 1}"
    return f"{today.year - 1}/{today.year}"
from apps.inscription.models import Inscription, ModuleChoisi
from apps.notes.models import Note


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

        # --- 18 MODULES DU CATALOGUE (12 premiers totalisent 60, 6 supplémentaires pour tester dépassement)
        modules_data = [
            ("Algorithmique et Problem Solving", 5, "Résolution de problèmes complexes, analyse algorithmique, structures de données avancées"),
            ("Conception orientée objet et programmation Java", 6, "POO, héritage, polymorphisme, Java, design patterns"),
            ("Data warehousing", 4, "Entrepôts de données, ETL, modélisation dimensionnelle, OLAP"),
            ("Framework Python pour le web", 6, "Django, ORM, vues, templates, formulaires, déploiement"),
            ("Fundamentals on Deep Learning", 4, "Réseaux de neurones, backpropagation, CNN, RNN"),
            ("Génie logiciel", 6, "Méthodes agiles, UML, gestion de projet, qualité logicielle"),
            ("Machine Learning basics", 5, "Régression, classification, clustering, évaluation de modèles"),
            ("Multimodal AI", 4, "IA multimodale, fusion de données, vision et langage"),
            ("Python pour l'ingénierie des données", 5, "Pandas, NumPy, scraping, visualisation, pipelines"),
            ("Système de gestion de base de données", 5, "SQL avancé, optimisation, transactions, indexation"),
            ("Techniques d'estimation pour l'ingénieur", 5, "Estimation de coûts, analyse de risques, prévision"),
            ("Techniques d'optimisation", 5, "Programmation linéaire, optimisation combinatoire, algorithmes gloutons"),
            # Modules supplémentaires pour tester le dépassement de la limite des 60 points
            ("Sécurité des systèmes d'information", 8, "Cryptographie, sécurité réseau, authentification, gestion des risques"),
            ("Cloud Computing et DevOps", 10, "Virtualisation, conteneurisation, CI/CD, orchestration, infrastructure as code"),
            ("Blockchain et applications décentralisées", 12, "Chaînes de blocs, contrats intelligents, consensus, DApps"),
            ("Internet des Objets (IoT)", 3, "Capteurs, protocoles IoT, embarqué, traitement de flux"),
            ("Big Data Analytics", 7, "Traitement distribué, Spark, Kafka, analyse en temps réel, data lake"),
            ("Cybersécurité offensive", 15, "Pentesting, analyse de vulnérabilités, forensique, reverse engineering"),
        ]
        modules = []
        for intitule, coeff, desc in modules_data:
            mod = CatalogueModule.objects.create(
                intitule=intitule, coefficient=coeff, description=desc
            )
            modules.append(mod)

        self.stdout.write(f"  [OK] {len(modules)} modules du catalogue crees")

        # --- CATÉGORIES D'ÉVALUATION — types variés par module ---
        categories_by_module = [
            # Indice 0-11 : modules du panier de base (12 premiers)
            [("CC", 40), ("EXAM", 60)],
            [("CC", 30), ("TP", 30), ("EXAM", 40)],
            [("CC", 40), ("Projet", 30), ("EXAM", 30)],
            [("TP", 40), ("Projet", 60)],
            [("CC", 20), ("EXAM", 50), ("Projet", 30)],
            [("CC", 30), ("EXAM", 40), ("TP", 30)],
            [("CC", 40), ("EXAM", 60)],
            [("CC", 30), ("Projet", 40), ("EXAM", 30)],
            [("TP", 50), ("Projet", 50)],
            [("CC", 40), ("EXAM", 60)],
            [("CC", 40), ("EXAM", 60)],
            [("CC", 40), ("EXAM", 60)],
            # Indice 12-17 : modules supplémentaires
            [("CC", 30), ("TP", 30), ("EXAM", 40)],
            [("TP", 50), ("Projet", 50)],
            [("CC", 20), ("Projet", 40), ("EXAM", 40)],
            [("CC", 40), ("EXAM", 60)],
            [("CC", 30), ("EXAM", 40), ("TP", 30)],
            [("TP", 40), ("Projet", 60)],
        ]
        for mod, cats in zip(modules, categories_by_module):
            for nom, poids in cats:
                CategorieEvaluation.objects.create(nom=nom, poids=poids, module=mod)

        self.stdout.write("  [OK] Categories d evaluation creees")

        # --- 3 INSCRIPTIONS ---
        annee = _annee_courante()
        ins1 = Inscription.objects.create(
            etudiant=etu1, annee_academique=annee, statut="verrouillee"
        )
        ins2 = Inscription.objects.create(
            etudiant=etu2, annee_academique=annee, statut="verrouillee"
        )
        ins3 = Inscription.objects.create(
            etudiant=etu3, annee_academique=annee, statut="ouverte"
        )

        self.stdout.write("  [OK] Inscriptions creees")

        # --- MODULES CHOISIS ---
        # etu1: les 12 premiers modules (total coefficients = 60)
        etu1_modules = modules[:12]  # 60 points

        # etu2: 10 modules (total coefficients = 50 - inscription partielle)
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
