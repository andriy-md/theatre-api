from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Genre
from theatre.serializers import GenreSerializer

GENRE_URL = reverse("theatre:genre-list")


def create_sample_genre(**params):
    defaults = {
        "name": "Sample Genre"
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


def genre_detail_url(pk: int):
    return reverse("theatre:genre-detail", args=[pk])


class UnAuthenticatedGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(GENRE_URL)
        self.assertEqual(response.status_code, 401)


class AuthenticatedGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="test_user",
            password="qwer1234"
        )
        self.client.force_authenticate(user)

    def test_list_genres(self):
        create_sample_genre()
        create_sample_genre()

        response = self.client.get(GENRE_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_genre(self):
        genre = create_sample_genre()
        url = genre_detail_url(genre.id)

        response = self.client.get(url)
        serializer = GenreSerializer(genre)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="admin_user",
            password="qwer1234",
            is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_genre(self):
        payload = {"name": "brand new genre"}
        response = self.client.post(GENRE_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Genre.objects.get(name="brand new genre"))

    def test_put_genre(self):
        genre = create_sample_genre()
        url = genre_detail_url(genre.id)
        payload = {"name": "brand new"}

        response = self.client.put(url, data=payload)
        genre.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(genre.name, "brand new")

    def test_patch_genre(self):
        genre = create_sample_genre()
        url = genre_detail_url(genre.id)
        payload = {"name": "brand new"}

        response = self.client.patch(url, data=payload)
        genre.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(genre.name, "brand new")
