from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor
from theatre.serializers import ActorSerializer

ACTOR_URL = reverse("theatre:actor-list")


def create_sample_actor(**params):
    defaults = {
        "first_name": "Sample",
        "last_name": "Sampleson"
    }
    defaults.update(params)
    return Actor.objects.create(**defaults)


def actor_detail_url(pk: int):
    return reverse("theatre:actor-detail", args=[pk])


class UnAuthenticatedGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ACTOR_URL)
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
        create_sample_actor()
        create_sample_actor()

        response = self.client.get(ACTOR_URL)
        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_actor(self):
        actor = create_sample_actor()
        url = actor_detail_url(actor.id)

        response = self.client.get(url)
        serializer = ActorSerializer(actor)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_access_denied(self):
        payload = {
            "first_name": "Brad",
            "last_name": "Pitt"
        }
        response = self.client.put(ACTOR_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            username="admin_user",
            password="qwer1234",
            is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_actor(self):
        payload = {
            "first_name": "Brad",
            "last_name": "Pitt"
        }
        response = self.client.post(ACTOR_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Actor.objects.get(first_name="Brad"))

    def test_put_actor(self):
        actor = create_sample_actor()
        url = actor_detail_url(actor.id)
        payload = {
            "first_name": "Leo",
            "last_name": "Smith"
        }

        response = self.client.put(url, data=payload)
        actor.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(getattr(actor, key), payload[key])

    def test_patch_actor(self):
        actor = create_sample_actor()
        url = actor_detail_url(actor.id)
        payload = {
            "first_name": "Leo",
            "last_name": "Smith"
        }

        response = self.client.patch(url, data=payload)
        actor.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(getattr(actor, key), payload[key])
