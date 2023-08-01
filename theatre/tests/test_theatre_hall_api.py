from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import TheatreHall
from theatre.serializers import TheatreHallSerializer

THEATRE_HALL_URL = reverse("theatre:theatrehall-list")


def create_sample_theatre_hall(**params):
    defaults = {"name": "Sample Theatre Hall", "rows": 8, "seats_in_row": 10}
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def theatre_hall_detail_url(pk: int):
    return reverse("theatre:theatrehall-detail", args=[pk])


class UnAuthenticatedTheatreHallApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(response.status_code, 401)


class AuthenticatedTheatreHallApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="test_user", password="qwer1234"
        )
        self.client.force_authenticate(user)

    def test_list_theatre_halls(self):
        create_sample_theatre_hall()
        create_sample_theatre_hall()

        response = self.client.get(THEATRE_HALL_URL)
        theater_halls = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theater_halls, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_theatre_hall(self):
        theatre_hall = create_sample_theatre_hall()
        url = theatre_hall_detail_url(theatre_hall.id)

        response = self.client.get(url)
        serializer = TheatreHallSerializer(theatre_hall)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminTheatreHallApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="admin_user", password="qwer1234", is_staff=True
        )
        self.client.force_authenticate(user)

    def test_put_theatre_hall(self):
        theatre_hall = create_sample_theatre_hall()
        url = theatre_hall_detail_url(theatre_hall.id)

        payload = {
            "name": "Newly Created Hall",
            "rows": 10,
            "seats_in_row": 12,
        }

        response = self.client.put(url, data=payload)
        theatre_hall.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            self.assertEqual(getattr(theatre_hall, key), payload[key])
        self.assertEqual(theatre_hall.capacity, 120)

    def test_patch_theatre_hall(self):
        theatre_hall = create_sample_theatre_hall()
        url = theatre_hall_detail_url(theatre_hall.id)
        payload = {
            "name": "Newly Created Hall",
            "rows": 10,
            "seats_in_row": 12,
        }

        response = self.client.patch(url, data=payload)
        theatre_hall.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            self.assertEqual(getattr(theatre_hall, key), payload[key])
        self.assertEqual(theatre_hall.capacity, 120)

    def test_create_theatre_hall(self):
        payload = {
            "name": "Newly Created Hall",
            "rows": 10,
            "seats_in_row": 12,
        }
        response = self.client.post(THEATRE_HALL_URL, data=payload)
        theatre_hall = TheatreHall.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(getattr(theatre_hall, key), payload[key])
        self.assertEqual(theatre_hall.capacity, 120)
