from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, TheatreHall, Performance
from theatre.serializers import PerformanceSerializer, PerformanceListRetrieveSerializer

PERFORMANCE_URL = reverse("theatre:performance-list")
DT = datetime.strptime("2023-08-01 19:00", "%Y-%m-%d %H:%M")


def create_sample_play(**params):
    defaults = {"title": "Sample Play", "description": "Best Play Ever"}
    defaults.update(params)
    return Play.objects.create(**defaults)


def create_sample_theatre_hall(**params):
    defaults = {"name": "Sample Theatre Hall", "rows": 8, "seats_in_row": 10}
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def create_sample_performance(**params):
    play1 = create_sample_play()
    theatre_hall1 = create_sample_theatre_hall()
    defaults = {"play": play1, "theatre_hall": theatre_hall1, "show_time": DT}
    defaults.update(params)
    return Performance.objects.create(**defaults)


def performance_detail_url(pk: int):
    return reverse("theatre:performance-detail", args=[pk])


class UnAuthenticatedPerformanceApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, 401)


class AuthenticatedPerformanceApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="test_user", password="qwer1234"
        )
        self.client.force_authenticate(user)

    def test_list_performance(self):
        create_sample_performance()
        create_sample_performance()

        response = self.client.get(PERFORMANCE_URL)
        performances = Performance.objects.all()
        serializer = PerformanceListRetrieveSerializer(performances, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_performance(self):
        performance = create_sample_performance()
        url = performance_detail_url(performance.id)

        response = self.client.get(url)
        serializer = PerformanceListRetrieveSerializer(performance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminPerformanceApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="admin_user", password="qwer1234", is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_performance(self):
        play1 = create_sample_play()
        theatre_hall1 = create_sample_theatre_hall()
        payload = {
            "play": play1.id,
            "theatre_hall": theatre_hall1.id,
            "show_time": DT,
        }
        response = self.client.post(PERFORMANCE_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Performance.objects.get(play=play1))

    def test_put_performance(self):
        performance = create_sample_performance()
        url = performance_detail_url(performance.id)
        play2 = create_sample_play(title="New Play", description="New Pla description")
        theatre_hall2 = create_sample_theatre_hall(
            name="New Theatre Hall", rows=8, seats_in_row=10
        )
        payload = {"play": play2.id, "theatre_hall": theatre_hall2.id, "show_time": DT}

        response = self.client.put(url, data=payload)
        performance.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(performance.play.title, "New Play")

    def test_patch_play(self):
        performance = create_sample_performance()
        play2 = create_sample_play(
            title="Patched Play", description="New Pla description"
        )
        url = performance_detail_url(performance.id)
        payload = {
            "play": play2.id,
        }

        response = self.client.patch(url, data=payload)
        performance.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(performance.play.title, "Patched Play")
