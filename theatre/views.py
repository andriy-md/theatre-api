from rest_framework import viewsets, views, status

from theatre.models import Genre, Actor, Play, TheatreHall, Reservation, Performance
from theatre.serializers import GenreSerializer, ActorSerializer, PlaySerializer, PlayListRetrieveSerializer, \
    TheatreHallSerializer, ReservationSerializer, PerformanceSerializer, PerformanceListRetrieveSerializer


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


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PerformanceListRetrieveSerializer
        return PerformanceSerializer
