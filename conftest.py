import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from plants.models import Plant, PlantType, Family, Nursery

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_api_client(admin_user):
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="regular_user",
        email="user@greencorner.ua",
        password="StrongPassword123!"
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_user",
        email="admin@greencorner.ua",
        password="AdminPassword123!"
    )


@pytest.fixture
def auth_client(api_client, regular_user):
    refresh = RefreshToken.for_user(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def plant_dependencies(db):
    plant_type = PlantType.objects.create(name="Декоративно-листяні")
    family = Family.objects.create(name="Ароїдні")
    nursery = Nursery.objects.create(name="Зелений Світ")
    return {
        "type": plant_type,
        "family": family,
        "nursery": nursery,
    }


@pytest.fixture
def sample_plant(db, plant_dependencies, regular_user):
    return Plant.objects.create(
        name="Монстера",
        latin_name="Monstera deliciosa",
        price=450,
        stock=10,
        light_level="medium",
        difficulty="easy",
        pet_safe=False,
        type=plant_dependencies["type"],
        family=plant_dependencies["family"],
        nursery=plant_dependencies["nursery"],
    )