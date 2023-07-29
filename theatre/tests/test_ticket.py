from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, TheatreHall, Performance, Ticket
from theatre.serializers import TicketListRetrieveSerializer

TICKET_URL = reverse("theatre:ticket-list")
DT = datetime.strptime("2023-08-01 19:00", "%Y-%m-%d %H:%M")


def create_sample_play(**params):
    defaults = {
        "title": "Sample Play",
        "description": "Best Play Ever"
    }
    defaults.update(params)
    return Play.objects.create(**defaults)


def create_sample_theatre_hall(**params):
    defaults = {
        "name": "Sample Theatre Hall",
        "rows": 8,
        "seats_in_row": 10
    }
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def create_sample_performance(**params):
    play1 = create_sample_play()
    theatre_hall1 = create_sample_theatre_hall()
    defaults = {
        "play": play1,
        "theatre_hall": theatre_hall1,
        "show_time": DT
    }
    defaults.update(params)
    return Performance.objects.create(**defaults)


def create_sample_ticket(**params):
    performance = create_sample_performance()
    defaults = {
        "row": 3,
        "seat": 5,
        "performance": performance
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


def ticket_detail_url(pk: int):
    return reverse("theatre:ticket-detail", args=[pk])


class AuthenticatedTicketApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_ticket(self):
        create_sample_ticket()
        create_sample_ticket()

        response = self.client.get(TICKET_URL)
        tickets = Ticket.objects.all()
        serializer = TicketListRetrieveSerializer(tickets, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_ticket(self):
        performance = create_sample_performance()
        payload = {
            "row": 3,
            "seat": 5,
            "performance": performance.id,
            "reservation": ""
        }
        response = self.client.post(TICKET_URL, data=payload)
        ticket = Ticket.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ticket.performance, performance)
        self.assertEqual(3, ticket.row)
        self.assertEqual(5, ticket.seat)

    def test_raises_error_if_row_out_of_range(self):
        performance = create_sample_performance()
        payload = {
            "row": 199,
            "seat": 5,
            "performance": performance.id,
            "reservation": ""
        }
        response = self.client.post(TICKET_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raises_error_if_seat_out_of_range(self):
        performance = create_sample_performance()
        payload = {
            "row": 2,
            "seat": 99,
            "performance": performance.id,
            "reservation": ""
        }
        response = self.client.post(TICKET_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ticket(self):
        ticket = create_sample_ticket()
        url = ticket_detail_url(ticket.id)

        response = self.client.get(url)
        serializer = TicketListRetrieveSerializer(ticket)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_ticket(self):
        ticket = create_sample_ticket()
        url = ticket_detail_url(ticket.id)
        performance1 = create_sample_performance()
        payload = {
            "row": 1,
            "seat": 2,
            "performance": performance1.id,
            "reservation": ""
        }
        response = self.client.put(url, data=payload)
        ticket.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ticket.performance, performance1)
        self.assertEqual(1, ticket.row)
        self.assertEqual(2, ticket.seat)

    def test_patch_ticket(self):
        ticket = create_sample_ticket()
        url = ticket_detail_url(ticket.id)
        performance = create_sample_performance()
        payload = {
            "row": 1,
            "performance": performance.id
        }

        response = self.client.patch(url, data=payload)
        ticket.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ticket.row, 1)
        self.assertEqual(ticket.performance, performance)
