from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Reservation
from theatre.serializers import ReservationSerializer

RESERVATION_URL = reverse("theatre:reservation-list")


def reservation_detail_url(pk: int):
    return reverse("theatre:reservation-detail", args=[pk])


class AuthenticatedReservationApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create(username="user1", password="qwerty1234")
        self.client.force_authenticate(self.user1)
        self.user2 = get_user_model().objects.create(username="user2", password="qwerty1234")
        self.client.force_authenticate(self.user2)

    def test_list_reservations(self):
        Reservation.objects.create(user=self.user1)
        Reservation.objects.create(user=self.user2)
        response = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_reservation(self):
        payload = {"user": self.user1.id}
        response = self.client.post(RESERVATION_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reservation.objects.get(user__username="user1"))

    def test_retrieve_reservation(self):
        reservation = Reservation.objects.create(user=self.user1)
        url = reservation_detail_url(reservation.id)

        response = self.client.get(url)
        serializer = ReservationSerializer(reservation)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_reservation(self):
        reservation = Reservation.objects.create(user=self.user1)
        url = reservation_detail_url(reservation.id)
        payload = {"user": self.user2.id}

        response = self.client.put(url, data=payload)
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reservation.user.username, "user2")

    def test_patch_reservation(self):
        reservation = Reservation.objects.create(user=self.user1)
        url = reservation_detail_url(reservation.id)
        payload = {"user": self.user2.id}

        response = self.client.patch(url, data=payload)
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reservation.user.username, "user2")
