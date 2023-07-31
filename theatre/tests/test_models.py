from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from theatre.models import Genre, Actor, Play, TheatreHall, Performance, Ticket, Reservation


def create_sample_genre(**params):
    defaults = {
        "name": "drama"
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


def create_sample_actor(**params):
    defaults = {
        "first_name": "Adam",
        "last_name": "Sandler"
    }
    defaults.update(params)
    return Actor.objects.create(**defaults)


def create_sample_play(**params):
    actor1 = create_sample_actor()
    actor2 = create_sample_actor(
        first_name="Ben",
        last_name="Smith"
    )
    genre1 = create_sample_genre()
    defaults = {
        "title": "Hamlet",
        "description": "Best drama of Shakespeare",
    }
    defaults.update(params)

    play = Play.objects.create(**defaults)
    play.actors.add(actor1, actor2)
    play.genres.add(genre1)

    return play


def create_sample_theatre_hall(**params):
    defaults = {
        "name": "Sample Hall",
        "rows": 8,
        "seats_in_row": 10
    }
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


def create_sample_performance(**params):
    play = create_sample_play()
    theatre_hall = create_sample_theatre_hall()
    dt = datetime.strptime("2023-08-01 19:00", "%Y-%m-%d %H:%M")

    defaults = {
        "play": play,
        "theatre_hall": theatre_hall,
        "show_time": dt
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def create_sample_reservation(user):
    return Reservation.objects.create(
        user=user
    )


def create_sample_ticket(reservation, **params):
    performance = create_sample_performance()
    defaults = {
        "row": 3,
        "seat": 5,
        "performance": performance,
        "reservation": reservation
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_sample_genre()

    def test_genre_str_works_correctly(self):
        genre = Genre.objects.get(id=1)

        self.assertEqual(str(genre), "drama")


class ActorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_sample_actor()

    def test_actor_str_works_correctly(self):
        actor = Actor.objects.get(id=1)

        self.assertEqual(str(actor), "Adam Sandler")


class PlayModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_sample_play()

    def test_play_str_works_correctly(self):
        play = Play.objects.get(id=1)

        self.assertEqual(str(play), play.title)


class TheatreHallModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_sample_theatre_hall()

    def test_theatre_hall_str_works_correctly(self):
        theatre_hall = TheatreHall.objects.get(id=1)

        self.assertEqual(str(theatre_hall), "Sample Hall (80)")

    def test_incorrect_row_count_raises_error(self):
        theatre_hall = create_sample_theatre_hall(rows=0)
        with self.assertRaises(ValidationError):
            theatre_hall.full_clean()


class TicketModelTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(
            username="test_user",
            password="qwer1234"
        )
        reservation = create_sample_reservation(self.user)
        create_sample_ticket(reservation)

    def test_ticket_str_works_correctly(self):
        ticket = Ticket.objects.get(id=1)
        self.assertEqual(
            str(ticket),
            "Hamlet Sample Hall: row 3 seat 5"
        )

    def test_ticket_seat_in_range_of_theatre_hall(self):
        reservation = create_sample_reservation(self.user)
        with self.assertRaises(ValidationError):
            create_sample_ticket(seat=32, row=42, reservation=reservation)
