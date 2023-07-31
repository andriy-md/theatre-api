from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlayListRetrieveSerializer, PlaySerializer

PLAY_URL = reverse("theatre:play-list")


def create_sample_genre(**params):
    defaults = {
        "name": "drama"
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


def create_sample_play(**params):
    defaults = {
        "title": "Sample Play",
        "description": "Best Play Ever",
    }
    defaults.update(params)
    return Play.objects.create(**defaults)


def play_detail_url(pk: int):
    return reverse("theatre:play-detail", args=[pk])


class UnAuthenticatedPlayApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PLAY_URL)
        self.assertEqual(response.status_code, 401)


class AuthenticatedPlayApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="test_user",
            password="qwer1234"
        )
        self.client.force_authenticate(user)

    def test_list_plays(self):
        create_sample_play()
        create_sample_play()

        response = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListRetrieveSerializer(plays, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_plays_by_title(self):
        play1 = create_sample_play()
        create_sample_play()
        searched_play = create_sample_play(title="The Searched One")

        response = self.client.get(PLAY_URL, {"title": "searched"})
        serializer_not_searched = PlayListRetrieveSerializer(play1)
        serializer_searched = PlayListRetrieveSerializer(searched_play)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_searched.data, response.data)
        self.assertNotIn(serializer_not_searched, response.data)

    def test_filter_plays_by_genre(self):
        genre1 = create_sample_genre()
        genre_searched = create_sample_genre(name="Searched genre")
        play1 = create_sample_play()
        play1.genres.add(genre1)
        create_sample_play()
        searched_play = create_sample_play()
        searched_play.genres.add(genre_searched)

        response = self.client.get(PLAY_URL, {"genre": "searched"})
        serializer_not_searched = PlayListRetrieveSerializer(play1)
        serializer_searched = PlayListRetrieveSerializer(searched_play)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_searched.data, response.data)
        self.assertNotIn(serializer_not_searched.data, response.data)

    def test_retrieve_play(self):
        play = create_sample_play()
        url = play_detail_url(play.id)

        response = self.client.get(url)
        serializer = PlayListRetrieveSerializer(play)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminPlayApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="admin_user",
            password="qwer1234",
            is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_play(self):
        genre = Genre.objects.create(name="Sample genre")
        actor = Actor.objects.create(first_name="Ben", last_name="Beninsen")
        payload = {
            "title": "Interesting test play",
            "description": "You want to visit this",
            "genres": [genre.id],
            "actors": [actor.id]
        }
        response = self.client.post(PLAY_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Play.objects.get(title="Interesting test play"))

    def test_put_play(self):
        play = create_sample_play()
        url = play_detail_url(play.id)
        genre = Genre.objects.create(name="Sample genre")
        actor = Actor.objects.create(first_name="Ben", last_name="Beninsen")
        payload = {
            "title": "new play",
            "description": "You want to visit this",
            "genres": [genre.id],
            "actors": [actor.id]
        }

        response = self.client.put(url, data=payload)
        play.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(play.title, "new play")

    def test_patch_play(self):
        play = create_sample_play()
        url = play_detail_url(play.id)
        payload = {
            "title": "Patched play",
            "description": "You want to visit this"
        }

        response = self.client.patch(url, data=payload)
        play.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(play.title, "Patched play")
