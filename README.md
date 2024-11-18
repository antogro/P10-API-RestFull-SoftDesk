# SoftDesk - API Rest Full

## 🌟 Introduction

SoftDesk est une application web qui permet de gérer des projets, des tickets d'assistance et des commentaires associés.
Cette application est construite avec le framework Django Rest Framework (DRF) et utilise une architecture d'API REST.

## ✨ Fonctionnalités

- Gestion des projets avec :
  - Titre
  - Description
  - Type
  - Date de création

- Gestion des contributeurs pour chaque projet
- Gestion des tickets (issues) avec :
  - Titre
  - Description
  - Priorité
  - Statut
  - Date de création

- Gestion des commentaires associés aux tickets
  - Uuid
  - Texte
  - Date de création

## 📊 Modèles de Données

### Modèle Project
- `title` : Titre du projet
- `description` : Description du projet
- `type` : Type de projet
- `created_time` : Date de création du projet
- `author` : Utilisateur qui a créé le projet (relation 1-N)
- `contributors` : Liste des contributeurs du projet (relation M-N)

### Modèle Issue
- `title` : Titre du ticket
- `description` : Description du ticket
- `priority` : Priorité du ticket
- `status` : Statut du ticket
- `created_time` : Date de création du ticket
- `author` : Utilisateur qui a créé le ticket (relation 1-N)
- `project` : Projet auquel le ticket est associé (relation 1-N)

### Modèle Comment
- `description` : Contenu du commentaire
- `created_time` : Date de création du commentaire
- `author` : Utilisateur qui a écrit le commentaire (relation 1-N)
- `issue` : Ticket auquel le commentaire est associé (relation 1-N)

### Modèle Contributor
- `user` : Utilisateur qui est contributeur (relation 1-N)
- `project` : Projet auquel l'utilisateur est contributeur (relation 1-N)
- `role` : Rôle du contributeur (non implémenté dans cette version)

### Modèle User
- `can_be_contacted` : Indique si l'utilisateur peut être contacté
- `can_data_be_shared` : Indique si les données de l'utilisateur peuvent être partagées
- `age` : Âge de l'utilisateur

## 🌐 API Endpoints

L'application expose les endpoints suivants :

- `/api/projects/` : Gestion des projets
- `/api/projects/<project_pk>/contributors/` : Gestion des contributeurs
- `/api/projects/<project_pk>/issues/` : Gestion des tickets
- `/api/projects/<project_pk>/issues/<issue_pk>/comments/` : Gestion des commentaires

## 🔒 Sécurité et Authentification

- Authentification via le système Django
- Seuls les utilisateurs authentifiés peuvent accéder à l'API
- Permissions spécifiques :
  - Seul l'auteur peut mettre à jour/supprimer un projet
  - Seuls les contributeurs peuvent gérer les tickets et commentaires

## 🚀 Installation

### Prérequis

- Python 3.9+
- pip
- pipenv (pour gérer les dépendances)

### Étapes d'installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-compte/SoftDesk.git
```

    Accédez au répertoire du projet :

```bash
cd SoftDesk
```
    Installez les dépendances avec pipenv :
```bash
pipenv install
```
    Configurez les variables d'environnement :

```bash
# Créez un fichier .env à la racine du projet
DEBUG=True
SECRET_KEY=votre-cle-secrete
DATABASE_URL=sqlite:///db.sqlite3
```
    Initialisez la base de données :

```bash
pipenv run python manage.py migrate
pipenv run python manage.py createsuperuser
```
    Lancez le serveur :

```bash
python manage.py runserver
```
🔍 Utilisation de l'API

Accédez à l'API à l'adresse : http://127.0.0.1:8000/api/

Exemple de requête :

```bash
curl http://127.0.0.1:8000/api/projects/ \

     -H "Authorization: Token votre-jeton-d-authentification"
```