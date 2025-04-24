[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-8d7812.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Django 5.1.8](https://img.shields.io/badge/5.1.8-Django-0c4b33)](https://www.djangoproject.com/)
[![Django Rest Framework 3.16.0](https://img.shields.io/badge/3.16.0-DRF-ad0000)](https://www.django-rest-framework.org/)

# Bookaloo

Lightweight REST API for managing library book inventory and borrow tracking, built with Django and DRF. For the sake of simplicity, permissions are non-existent in this project - all API endpoints are publicly available.

### Running the project locally

```bash
docker compose up
```

Once the app is running, you can access OpenAPI schema (swagger UI) on `127.0.0.1:8000`.

### Test data

You can generate some test data with:
```bash
docker compose run --rm django python3 manage.py test_data`
```

### Running tests

```bash
docker compose run --rm django pytest
```
