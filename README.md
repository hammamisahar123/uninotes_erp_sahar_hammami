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

## Modules du catalogue (18 modules, max 60 points par étudiant)

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
| Sécurité des systèmes d'information | 8 |
| Cloud Computing et DevOps | 10 |
| Blockchain et applications décentralisées | 12 |
| Internet des Objets (IoT) | 3 |
| Big Data Analytics | 7 |
| Cybersécurité offensive | 15 |

## Gestion de l'intégrité référentielle (3.B.5)

Deux stratégies sont implémentées pour protéger les données lors de la suppression d'un module du catalogue :

### 1. Protection par contrainte de clé étrangère (PROTECT)

La clé étrangère `module_catalogue` dans le modèle `ModuleChoisi` utilise `on_delete=models.PROTECT`.  
Toute tentative de suppression d'un `CatalogueModule` référencé par au moins un `ModuleChoisi` déclenche une `ProtectedError`.

**Comportement dans l'interface d'administration :**
- La méthode `delete_model()` de `CatalogueModuleAdmin` intercepte l'erreur et affiche un message d'erreur explicite indiquant le nombre de choix d'étudiants concernés.
- La méthode `delete_queryset()` gère les suppressions en lot avec le même mécanisme.
- L'administrateur est invité à utiliser l'archivage comme alternative.

### 2. Archivage via le champ `est_actif`

Le champ booléen `est_actif` (défaut : `True`) sur `CatalogueModule` permet de masquer un module sans le supprimer :

- Dans l'admin, décocher la case "Actif" dans la liste ou modifier le champ dans le formulaire de détail.
- Les modules inactifs sont exclus de l'affichage dans le catalogue (`catalogue/views.py`), le panier (`inscription/services.py`) et la suggestion de modules.
- Les données existantes (`ModuleChoisi`, `Note`, moyennes) sont intégralement conservées.
- Les étudiants ayant déjà sélectionné le module conservent leur choix et leurs notes. 
- Le module reste accessible en requêtage direct via l'ORM si nécessaire (ex. re-calcul de moyennes historiques).

## Limites et améliorations possibles

- Interface utilisateur basique (CSS minimal) — amélioration possible avec Bootstrap/Tailwind
- Pas d'API REST — limitation volontaire (hors périmètre)
- Pas de tests automatisés — à ajouter pour la logique métier
- Pas de déploiement — projet local uniquement
