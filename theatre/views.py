from rest_framework import viewsets, views, status

from theatre.models import Genre, Actor, Play
from theatre.serializers import GenreSerializer, ActorSerializer, PlaySerializer, PlayListRetrieveSerializer


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class ActorViewSet(viewsets.ModelViewSet):
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PlayListRetrieveSerializer
        return PlaySerializer
