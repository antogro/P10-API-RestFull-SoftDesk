# SoftDesk - API REST pour la Gestion de Projets 🚀

## 📖 Table des Matières
1. [Introduction](#introduction)
2. [Technologies Utilisées](#technologies-utilisées)
3. [Installation en Développement](#installation)
4. [Fonctionnalités](#fonctionnalités)
5. [Architecture des Données](#architecture-des-données)
6. [API Endpoints](#api-endpoints)
7. [Authentification et Sécurité](#authentification-et-sécurité)
8. [Installation](#installation)
9. [Exemples d'Utilisation avec Postman](#exemples-dutilisation-avec-postman)
10. [Gestion des Erreurs](#gestion-des-erreurs)
11. [Auteur](#auteur)



## 📖 Introduction

SoftDesk est une solution professionnelle de gestion de projets et de support technique, conçue pour optimiser la collaboration des équipes de développement. Cette API REST, construite avec Django Rest Framework, permet de :

- Gérer efficacement les projets et leurs équipes
- Suivre et résoudre les problèmes via un système de tickets (Issue)
- Faciliter la communication avec un système de commentaires

## 🛠 Technologies Utilisées

- **Backend Framework**: Django 5.1.3
- **API Framework**: Django Rest Framework 3.14+
- **Base de données**: SQLite (développement) / PostgreSQL (production recommandée)
- **Authentication**: JWT (JSON Web Tokens)

## 🚀 Installation

### Prérequis
- Python 3.9+
- pip
- git
- Pipenv

### Installation en Développement

1. **Cloner le projet**
```bash
git clone https://github.com/antogro/P10-API-RestFull-SoftDesk.git
cd P10-API-RestFull-SoftDesk
```

2. **Configurer l'environnement avec Pipenv**
```bash
# Installer Pipenv si nécessaire
pip install pipenv

# Installer les dépendances avec Pipenv
python -m pipenv install

# Activer l'environnement virtuel
pipenv shell
```

3. **Initialiser la base de données**
```bash
cd config
python manage.py migrate
python manage.py createsuperuser
```

4. **Lancer le serveur de développement**
```bash
python manage.py runserver
```
*Explication* : Cette commande démarre le serveur de développement Django,
qui vous permet d'accéder à l'application localement via votre navigateur à
l'adresse suivante : **http://127.0.0.1:8000/**. Vous pouvez l'utiliser pour tester
l'application sur votre machine avant de la déployer en production.

## ✨ Fonctionnalités

### Gestion de Projets
- Création et gestion de projets avec métadonnées complètes
- Selection du type de projet (Back-end, Front-end, IOS, Android)
- Système de permissions basé sur les rôles :
    - Auteur pour la lecture, la modification, et la suppression des projets
    - Contributeur pour la lecture des projets

### Gestion des Issues
- Système de priorité configurable (Faible, Moyen, Elevé)
- Statuts personnalisables (À faire, En cours, Terminé)
- Tag personnalisables (Bug, fonctionnalité, Tâche)
- Attribution à un membre des contributeurs du projet
- lié à un projet

### Système de Commentaires
- Fils de discussion par Issue
- Commentaires avec possibilité d'éditer ou supprimer
- Lié à une Issue

### Gestion des contributeurs
- Ajout et gestion des contributeurs à un projet
- Lié à un projet

## 📊 Architecture des Données

### Modèle Project
```python
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE related_name='authored_projects')
```

## 🌐 API Endpoints

L'application expose les endpoints suivants :

- `/api/projects/` : Gestion des projets
- `/api/projects/<project_pk>/contributors/` : Gestion des contributeurs
- `/api/projects/<project_pk>/issues/` : Gestion des tickets
- `/api/projects/<project_pk>/issues/<issue_pk>/comments/` : Gestion des commentaires

#### Exemple de Réponse (GET /api/projects/)
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Projet Test",
            "description": "Description du projet",
            "type": "BACKEND",
            "created_time": "2024-03-19T14:30:00Z",
            "author": {
                "id": 1,
                "username": "john_doe"
            },
            "contributors_count": 3
        }
    ]
}
```


## 🔒 Authentification et Sécurité

### Système d'Authentication
- Utilisation de JWT (JSON Web Tokens)
- Durée de validité des tokens : 1h
- Refresh token disponible pour renouvellement


### Exemple d'Authentication
```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/token/ \
    -H "Content-Type: application/json" \
    -d '{"username": "user", "password": "pass"}'

# Utiliser le token
curl -X GET http://localhost:8000/api/projects/ \
    -H "Authorization: Bearer <votre_token>"
```

### 🛡️ Sécurité

L'application répond aux exigences OWASP en matière de sécurité :

1. **Authentification et Autorisation**
   - Utilisation de JWT avec expiration
   - Validation des permissions à chaque requête
   - Protection contre les attaques par force brute

2. **Protection des Données**
   - Hashage sécurisé des mots de passe avec Django
   - Validation des données entrantes

3. **Conformité RGPD**
   - Consentement explicite pour la collecte de données
   - Possibilité de supprimer son compte
   - Contrôle des données partagées




## 📝 Exemples d'Utilisation avec Postman

### 1. Création d'un Utilisateur

#### Requête
- **URL**: `POST http://127.0.0.1:8000/api/users/`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body**:
  ```json
  {
    "username": "john_doe",
    "password": "Secure@Password123",
    "email": "john@example.com",
    "can_be_contacted": true,
    "can_data_be_shared": false,
    "age": 30
  }
  ```

#### Réponse
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "can_be_contacted": true,
  "can_data_be_shared": false
}
```

### 2. Authentification

#### Requête
- **URL**: `POST http://127.0.0.1:8000/api/token/`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body**:
  ```json
  {
    "username": "john_doe",
    "password": "Secure@Password123"
  }
  ```

#### Réponse
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Création d'un Projet (Authentifié)

#### Requête
- **URL**: `POST http://127.0.0.1:8000/api/projects/`
- **Headers**: 
  ```
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  Content-Type: application/json
  ```
- **Body**:
  ```json
  {
    "title": "Nouveau Projet",
    "description": "Description du projet",
    "type": "BACKEND"
  }
  ```

## 🐛 Gestion des Erreurs

| Code | Description | Solution |
|------|-------------|----------|
| 401 | Non authentifié | Vérifier le token d'authentification |
| 403 | Non autorisé | Vérifier les permissions de l'utilisateur |
| 404 | Ressource non trouvée | Vérifier l'ID de la ressource |
| 500 | Erreur serveur | Contacter l'administrateur |


## 👤 Auteur
Développé par [antogro](https://github.com/antogro/)

