from rest_framework import viewsets, views, status

from theatre.models import Genre, Actor
from theatre.serializers import GenreSerializer, ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class ActorViewSet(viewsets.ModelViewSet):
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()
