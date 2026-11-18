import pytest
from rest_framework import status
from plants.models import Plant

# get tests


def test_get_plants_list_success(api_client, sample_plant):
    url = "/api/plants/"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.data if isinstance(response.data, list) else response.data.get("results", response.data.get("items", []))
    assert len(data) >= 1
    assert data[0]["name"] == sample_plant.name


def test_get_plant_detail_success(api_client, sample_plant):
    url = f"/api/plants/{sample_plant.id}/"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Монстера"
    assert float(response.data["price"]) == 450.0


@pytest.mark.django_db
def test_get_plant_detail_not_found(api_client):
    url = "/api/plants/99999/"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

# post tests    


def test_create_plant_authenticated_success(auth_client, plant_dependencies):
    url = "/api/plants/"
    payload = {
        "name": "Фікус Бенджаміна",
        "latinName": "Ficus benjamina",
        "price": 320,
        "stock": 5,
        "lightLevel": "high",
        "difficulty": "medium",
        "petSafe": False,
        "typeId": plant_dependencies["type"].id,
        "familyId": plant_dependencies["family"].id,
        "nurseryId": plant_dependencies["nursery"].id,
    }

    response = auth_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Plant.objects.filter(name="Фікус Бенджаміна").exists()


def test_create_plant_unauthenticated_forbidden(api_client, plant_dependencies):
    url = "/api/plants/"
    payload = {
        "name": "Анонімний кактус",
        "price": 150,
        "stock": 3,
        "typeId": plant_dependencies["type"].id,
        "familyId": plant_dependencies["family"].id,
        "nurseryId": plant_dependencies["nursery"].id,
    }

    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Plant.objects.filter(name="Анонімний кактус").exists()


def test_create_plant_invalid_data_bad_request(auth_client):
    url = "/api/plants/"
    invalid_payload = {
        "name": "",
        "price": "некоректна_ціна",
        "stock": -5,
    }

    response = auth_client.post(url, data=invalid_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert "name" in response.data["error"]
    assert "price" in response.data["error"]


# put tests

def test_update_plant_success(auth_client, sample_plant, plant_dependencies):
    url = f"/api/plants/{sample_plant.id}/"
    put_data = {
        "name": "Монстера Оновлена",
        "latinName": "Monstera deliciosa",
        "price": 500,
        "stock": 8,
        "lightLevel": "medium",
        "difficulty": "easy",
        "petSafe": False,
        "typeId": plant_dependencies["type"].id,
        "familyId": plant_dependencies["family"].id,
        "nurseryId": plant_dependencies["nursery"].id,
    }

    response = auth_client.put(url, data=put_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    sample_plant.refresh_from_db()
    assert sample_plant.name == "Монстера Оновлена"
    assert float(sample_plant.price) == 500.0
    assert sample_plant.stock == 8


def test_update_plant_unauthenticated(api_client, sample_plant):
    url = f"/api/plants/{sample_plant.id}/"

    response = api_client.put(url, data={"name": "Хак"}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# delete tests

def test_delete_plant_success(admin_api_client, sample_plant):
    url = f"/api/plants/{sample_plant.id}/"

    response = admin_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Plant.objects.filter(id=sample_plant.id).exists()


def test_delete_plant_unauthenticated(api_client, sample_plant):
    url = f"/api/plants/{sample_plant.id}/"

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Plant.objects.filter(id=sample_plant.id).exists()


def test_delete_plant_not_found(admin_api_client):
    url = "/api/plants/99999/"

    response = admin_api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND