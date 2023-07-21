from django.test import TestCase

from theatre.models import Genre, Actor, Play


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name="drama")

    def test_genre_str_works_correctly(self):
        genre = Genre.objects.get(id=1)

        self.assertEqual(str(genre), "drama")


class ActorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Actor.objects.create(
            first_name="Adam",
            last_name="Sandler"
        )

    def test_actor_str_works_correctly(self):
        actor = Actor.objects.get(id=1)

        self.assertEqual(str(actor), "Adam Sandler")


class PlayModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Play.objects.create(
            title="Hamlet",
            description="Best drama of Shakespeare"
        )

    def test_play_str_works_correctly(self):
        play = Play.objects.get(id=1)

        self.assertEqual(str(play), play.title)
