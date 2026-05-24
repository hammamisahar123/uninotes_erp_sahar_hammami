# UniNotes ERP

Application web de suivi académique permettant à un étudiant de composer librement son année en sélectionnant des modules dans un catalogue (contrainte stricte de 60 points de coefficient), de saisir ses notes et de suivre son évolution.

**Mini-projet universitaire — Framework Django**  
**Date : Mai 2026**

## Fonctionnalités

- Inscription et authentification avec choix du rôle (étudiant / tuteur)
- Catalogue de modules consultable avec catégories d'évaluation
- Panier d'inscription avec compteur temps réel et verrouillage automatique à 60 points
- Moteur de suggestion automatique de modules (exacts puis possibles) selon les points restants
- Dashboard de suivi avec saisie des notes par catégorie d'évaluation
- Calcul des moyennes pondérées via ORM Django (annotate, aggregate, Sum, Case)
- Courbe d'évolution de la moyenne générale avec Chart.js (reconstitution historique)
- Accès tuteur en lecture seule aux données des étudiants parrainés
- Isolation des données par utilisateur
- Interface d'administration personnalisée (gestion des utilisateurs, modules, inscriptions, notes)
- Architecture structurée avec les apps Django dans un dossier `apps/`

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/hammamisahar123/uninotes_erp_sahar_hammami.git
cd uninotes_erp_sahar_hammami

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. (Optionnel) Installer Node.js et générer les styles Tailwind
npm install
npm run build:css

# 5. Appliquer les migrations
python manage.py migrate

# 6. Charger les données de test
python manage.py seed_data
#   Ré-exécuter avec --force pour remplacer les données existantes

# 7. (Optionnel) Créer un super-utilisateur pour l'admin
python manage.py createsuperuser

# 8. Lancer le serveur
python manage.py runserver
```

Puis ouvrir http://127.0.0.1:8000/

## Tests

```bash
python manage.py test
# 33 tests — modèles, services et gestionnaires
```

## Structure du projet

```
uninotes_erp_sahar_hammami/
├── apps/                  # Applications Django
│   ├── accounts/          # Gestion des profils utilisateurs (rôles, parrainage)
│   │   ├── models.py      # Profile (1-1 User, self-FK tuteur)
│   │   ├── services.py    # DashboardService (modules, notes par catégorie)
│   │   ├── decorators.py  # Decorateur @role_required
│   │   ├── forms.py       # SignupForm, LoginForm
│   │   ├── signals.py     # Création auto du Profile à l'inscription
│   │   ├── templatetags/  # Filtres personnalisés (dict_key, split)
│   │   ├── admin.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── catalogue/         # Référentiel (données de l'établissement)
│   │   ├── models.py      # CatalogueModule, CategorieEvaluation
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── inscription/       # Inscriptions et choix de modules
│   │   ├── models.py      # Inscription, ModuleChoisi
│   │   ├── managers.py    # ModuleChoisiQuerySet (with_moyenne, moyenne_générale)
│   │   ├── services.py    # PanierService (ajout/retrait/suggestions)
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tests.py
│   │   └── views.py
│   └── notes/             # Saisie des notes
│       ├── models.py      # Note
│       ├── managers.py    # NoteQuerySet (total_pondere)
│       ├── services.py    # NoteService, CourbeService
│       ├── urls.py
│       ├── admin.py
│       ├── tests.py
│       ├── views.py
│       └── management/commands/seed_data.py
├── uninotes_erp/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── admin_site.py      # AdminSite personnalisé
├── templates/             # Templates HTML
│   ├── base.html
│   ├── accounts/
│   │   └── home.html, dashboard.html
│   ├── catalogue/
│   │   └── liste.html
│   ├── inscription/
│   │   └── panier.html
│   ├── notes/
│   │   └── saisie_notes.html, courbe.html
│   └── registration/
│       └── login.html, signup.html
├── static/                # Fichiers statiques (CSS, JS)
│   ├── css/style.css
│   ├── js/main.js
│   └── admin/js/
│       ├── profile_role.js
│       └── poids_validation.js
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

## Année académique dynamique

L'année académique est calculée automatiquement à partir de la date du jour :

- **Septembre → Décembre** : `{année_courante}/{année_courante+1}` (ex: 2026/2027)
- **Janvier → Août** : `{année_courante-1}/{année_courante}` (ex: 2025/2026)

Disponible dans tous les templates via `{{ ANNEE_ACADEMIQUE }}`.

## Choix techniques

- **Framework** : Django 5.2.14
- **Base de données** : SQLite (db.sqlite3)
- **Authentification** : système natif Django (django.contrib.auth)
- **Graphiques** : Chart.js (CDN)
- **Front-end** : Templates Django + CSS natif + Tailwind CSS (généré via Node.js, `npm run build:css`)
- **Calculs** : ORM Django (annotate, aggregate, F, Sum, Case) pour les moyennes pondérées
- **Administration** : `AdminSite` personnalisé (`uninotes_erp/admin_site.py`) — conservé pour personnaliser l'en-tête et le titre, sans session séparée. L'admin et le site public partagent la même authentification (comportement Django par défaut), permettant aux super-utilisateurs (`sami.sifi`, `admin`) d'accéder aux deux interfaces avec une seule connexion.

## Comptes de test

### Administration

| Utilisateur | Rôle | Mot de passe |
|---|---|---|
| admin | Super-admin / Tuteur | admin123 |
| sami.sifi | Super-admin / Tuteur | sami123 |

URL : http://127.0.0.1:8000/admin/

### Tuteurs

| Utilisateur | Nom | Mot de passe |
|---|---|---|
| karim.mansour | Karim Mansour | tuteur123 |
| nadia.belhaj | Nadia Belhaj | tuteur123 |
| lotfi.gueddiche | Lotfi Gueddiche | tuteur123 |

### Étudiants

| Utilisateur | Mot de passe | Tuteur |
|---|---|---|
| ahmed.benali | etudiant123 | sami.sifi |
| sarah.trabelsi | etudiant123 | sami.sifi |
| mehdi.khalil | etudiant123 | sami.sifi |
| takwa_loueti | etudiant123 | Karim Mansour |

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

- Interface utilisateur basique (CSS natif + Tailwind) — amélioration possible avec Bootstrap
- Pas d'API REST — limitation volontaire (hors périmètre)
- Couverture de tests partielle — à étendre pour la logique métier avancée
- Pas de déploiement — projet local uniquement
