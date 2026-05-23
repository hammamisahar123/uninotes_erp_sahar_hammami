# UniNotes ERP

Application web de suivi académique permettant à un étudiant de composer librement son année en sélectionnant des modules dans un catalogue (contrainte stricte de 60 points de coefficient), de saisir ses notes et de suivre son évolution.

**Mini-projet universitaire — Framework Django**  
**Date : Mai 2026**

## Fonctionnalités

- Inscription et authentification avec choix du rôle (étudiant / tuteur)
- Catalogue de modules consultable avec catégories d'évaluation
- Panier d'inscription avec compteur temps réel et verrouillage automatique à 60 points
- Moteur de recommandation de modules selon les points restants
- Dashboard de suivi avec saisie des notes par catégorie d'évaluation
- Calcul des moyennes pondérées via ORM Django (annotate, aggregate)
- Courbe d'évolution de la moyenne générale (Chart.js)
- Accès tuteur en lecture seule aux données des étudiants parrainés
- Isolation des données par utilisateur

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/hammamisahar123/uninotes_erp_sahar_hammami.git
cd uninotes_erp_sahar_hammami

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. (Optionnel) Charger les données de test
python manage.py seed_data

# 6. Lancer le serveur
python manage.py runserver
```

Puis ouvrir http://127.0.0.1:8000/

## Structure du projet

```
uninotes_erp_sahar_hammami/
├── accounts/              # Gestion des profils utilisateurs (rôles, parrainage)
│   ├── models.py          # Profile (1-1 User, self-FK tuteur)
│   └── admin.py
├── catalogue/             # Référentiel (données de l'établissement)
│   ├── models.py          # CatalogueModule, CategorieEvaluation
│   └── admin.py
├── inscription/           # Inscriptions et choix de modules
│   ├── models.py          # Inscription, ModuleChoisi
│   └── admin.py
├── notes/                 # Saisie des notes
│   ├── models.py          # Note
│   ├── admin.py
│   └── management/commands/seed_data.py
├── uninotes_erp/          # Configuration Django
│   ├── settings.py
│   └── urls.py
├── templates/             # Templates HTML
├── static/                # Fichiers statiques (CSS, JS)
├── manage.py
├── requirements.txt
├── uninotes_erp_export.sql
└── README.md
```

## Modèle de données

### Référentiel (catalogue)
- **CatalogueModule** : intitulé, coefficient, description, est_actif
- **CategorieEvaluation** : nom, poids (%), module (FK)

### Données utilisateur
- **Profile** : user (1-1), rôle (étudiant/tuteur), tuteur (self-FK)
- **Inscription** : étudiant (FK), année académique, statut (ouverte/verrouillée)
- **ModuleChoisi** : inscription (FK), module_catalogue (FK)
- **Note** : module_choisi (FK), categorie_evaluation (FK), valeur, date_saisie

### Contraintes principales
- Somme des coefficients des modules choisis ≤ 60, verrouillage auto à 60 exactement
- Unicité : un même module ne peut être choisi deux fois dans une inscription
- Unicité : une seule note par couple (module_choisi, categorie_evaluation)
- Somme des poids des catégories d'un module = 100%
- Note valide entre 0 et 20 (deux décimales max)

## Choix techniques

- **Framework** : Django 5.2.14
- **Base de données** : SQLite (db.sqlite3)
- **Authentification** : système natif Django (django.contrib.auth)
- **Graphiques** : Chart.js (CDN)
- **Front-end** : Templates Django + CSS natif
- **Calculs** : ORM Django (annotate, aggregate, F, Sum) pour les moyennes pondérées

## Comptes de test

| Utilisateur | Rôle | Mot de passe |
|---|---|---|
| sami.sifi | Tuteur | password123 |
| ahmed.benali | Étudiant | password123 |
| sarah.trabelsi | Étudiant | password123 |
| mehdi.khalil | Étudiant | password123 |

## Modules du catalogue (12 modules, 60 points)

| Module | Coefficient |
|---|---|
| Algorithmique et Problem Solving | 5 |
| Conception orientée objet et programmation Java | 6 |
| Data warehousing | 4 |
| Framework Python pour le web | 6 |
| Fundamentals on Deep Learning | 4 |
| Génie logiciel | 6 |
| Machine Learning basics | 5 |
| Multimodal AI | 4 |
| Python pour l'ingénierie des données | 5 |
| Système de gestion de base de données | 5 |
| Techniques d'estimation pour l'ingénieur | 5 |
| Techniques d'optimisation | 5 |

## Gestion de l'intégrité référentielle

Stratégie choisie pour la suppression d'un module du catalogue :
- **Protection par contrainte de clé étrangère** : la suppression est refusée si le module est référencé par des choix d'étudiants.
- Alternative implémentée : archivage via le champ `est_actif` (le module est masqué du catalogue mais les données existantes sont préservées).

## Limites et améliorations possibles

- Interface utilisateur basique (CSS minimal) — amélioration possible avec Bootstrap/Tailwind
- Pas d'API REST — limitation volontaire (hors périmètre)
- Pas de tests automatisés — à ajouter pour la logique métier
- Pas de déploiement — projet local uniquement
