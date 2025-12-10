# Instravel — Backend Python + MySQL (CRUD)

Petit backend pédagogique pour gérer des utilisateurs et leurs voyages via MySQL.
Le code fournit des CRUD simples:
- `UsersCRUD` pour la table `users`
- `VoyagesCRUD` pour la table `voyages`
- `HashtagsCRUD` pour la table `hashtag`
- `EtapeHashtagCRUD` pour l'association `etape_hashtag` (liaison étapes ↔ hashtags)
- `AbonnementCRUD` pour la table `abonnement` (relations follower/followed)
- `PhotosCRUD` pour la table `photos`

La connexion MySQL s’appuie sur des variables d’environnement chargées depuis un fichier `.env`.

## Prérequis
- Windows avec PowerShell
- [Anaconda/Miniconda] pour utiliser `environment.yml`
- MySQL Server 8.x (ou compatible) installé et accessible en local

## Installation rapide
```powershell
# 1) Créer et activer l’environnement conda
conda env create -f environment.yml
conda activate instravel_env

# 2) Créer le fichier .env à la racine du projet
ni .env -ItemType File
```

Contenu recommandé pour `.env` (à adapter) :
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=app_voyage
```
Note: l’application force `localhost` → `127.0.0.1` sous Windows pour éviter Named Pipes.

## Base de données
Le dump SQL se trouve dans `db/dump-app_voyage-v1.sql`.

Créer la base et importer le schéma/données:
```powershell
# Crée la base si besoin
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS app_voyage CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"

# Importe le dump dans la base app_voyage
mysql -u root -p app_voyage < db\dump-app_voyage-v1.sql
```
Si vous préférez, vous pouvez aussi importer le fichier via MySQL Workbench (File > Run SQL Script…).

## Lancer les tests manuels (CRUD)
Exécuter depuis la racine du projet:
```powershell
# Tests CRUD users
python -m tests.test_users_crud

# Tests CRUD voyages (crée un user temporaire, puis le nettoie)
python -m tests.test_voyages_crud
```
Chaque script affiche les étapes: CREATE, GET, UPDATE, GET_ALL, DELETE.

## Tests supplémentaires
```powershell
# CRUD hashtags
python -m tests.test_hashtags_crud

# Association etape_hashtag – (placeholder tant que CRUD etapes absent)
python -m tests.test_etape_hashtag_crud

# CRUD abonnement (follow/unfollow/mutual)
python -m tests.test_abonnement_crud

# CRUD photos (nécessite un id_etape existant: ajuster test si CRUD etapes ajouté)
python -m tests.test_photos_crud

# Tous les tests unitaires Pytest (nouvelle suite)
pytest -q
```
## Structure du projet
- `backend/database.py` : gestion de la connexion MySQL (singleton) via `.env`
- `backend/crud/users.py` : opérations CRUD sur `users`
- `backend/crud/voyages.py` : opérations CRUD sur `voyages`
- `backend/crud/hashtags.py` : opérations CRUD sur `hashtags`
- `backend/crud/etape_hashtag.py` : opérations CRUD sur l'association `etape_hashtag`
- `backend/crud/abonnement.py` : opérations CRUD sur `abonnement`
- `backend/crud/photo.py` : opérations CRUD sur `photos`
- `db/dump-app_voyage-v1.sql` : schéma et FK des tables principales
- `tests/` : scripts de test manuels des CRUD
- `documentation/` : notes sur la base et les CRUD
	- `documentation/users_crud.md`
	- `documentation/voyage_crud.md`
	- `documentation/hashtags_crud.md`
	- `documentation/etape_hashtag_crud.md`
	- `documentation/abonnement_crud.md`
	- `documentation/photos_crud.md`
	- `documentation/etapes_crud.md`
	- `documentation/commentaire_hashtag_crud.md`

## Dépannage
- Connexion refusée: vérifier `.env` (hôte, port, user, mot de passe, nom de base)
- Sur Windows, utilisez `DB_HOST=127.0.0.1` plutôt que `localhost`
- Assurez-vous que MySQL est démarré et que l’utilisateur a les droits sur `app_voyage`

## Licence
Projet éducatif. Utiliser et adapter librement selon vos besoins.
