# SoftDesk Support API

API RESTful développée avec Django REST Framework pour le suivi de projets et de problèmes techniques.

## Prérequis

- Python 3.10 ou une version plus récente ;
- [Poetry](https://python-poetry.org/docs/#installation) pour la gestion des dépendances.

## Installation

Cloner le dépôt puis se placer dans le dossier du projet :

```bash
git clone URL_DU_DEPOT
cd softdesk-support-api
```

Installer les dépendances et créer l'environnement virtuel :

```bash
poetry install
```

Appliquer les migrations de la base de données :

```bash
poetry run python manage.py migrate
```

## Lancement

Démarrer le serveur de développement :

```bash
poetry run python manage.py runserver
```

L'application est alors accessible à l'adresse <http://127.0.0.1:8000/>.

## Tests

Lancer les tests avec la commande suivante :

```bash
poetry run python manage.py test
```
