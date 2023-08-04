from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Reservation, TheatreHall, Performance, Play, Ticket
from theatre.serializers import ReservationSerializer

RESERVATION_URL = reverse("theatre:reservation-list")
DT = datetime.strptime("2023-08-01 19:00", "%Y-%m-%d %H:%M")


def reservation_detail_url(pk: int):
    return reverse("theatre:reservation-detail", args=[pk])


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


class AuthenticatedPerformanceApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="test_user", password="qwer1234"
        )
        self.client.force_authenticate(user)


class AuthenticatedReservationApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create(
            username="user1", password="qwerty1234"
        )
        self.client.force_authenticate(self.user1)
        self.user2 = get_user_model().objects.create(
            username="user2", password="qwerty1234"
        )

    def test_list_reservations(self):
        Reservation.objects.create(user=self.user1)
        Reservation.objects.create(user=self.user1)
        Reservation.objects.create(user=self.user2)

        response = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.filter(user=self.user1)
        serializer = ReservationSerializer(reservations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminPerformanceApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="admin_user", password="qwer1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_reservation(self):
        create_sample_performance()
        payload = {"tickets": [{"row": 1, "seat": 2, "performance": 1}]}
        response = self.client.post(RESERVATION_URL, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reservation.objects.get(user__username="admin_user"))

    def test_raises_error_if_row_out_of_range(self):
        create_sample_performance()
        payload = {"tickets": [{"row": 199, "seat": 2, "performance": 1}]}

        response = self.client.post(RESERVATION_URL, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raises_error_if_seat_out_of_range(self):
        create_sample_performance()
        payload = {"tickets": [{"row": 1, "seat": 255, "performance": 1}]}

        response = self.client.post(RESERVATION_URL, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raises_error_if_same_seat_for_same_performance(self):
        performance = create_sample_performance()
        reservation1 = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            row=3, seat=4, performance=performance, reservation=reservation1
        )
        payload = {"tickets": [{"row": 3, "seat": 4, "performance": 1}]}

        response = self.client.post(RESERVATION_URL, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
