from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from theatre.models import Genre, Actor, Play, TheatreHall, Reservation, Performance
from theatre.serializers import GenreSerializer, ActorSerializer, PlaySerializer, PlayListRetrieveSerializer, \
    TheatreHallSerializer, ReservationSerializer, PerformanceSerializer, PerformanceListRetrieveSerializer, \
    ReservationListSerializer


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class ActorViewSet(viewsets.ModelViewSet):
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all().prefetch_related("actors", "genres")

    def get_queryset(self):
        """Search plays by title and genres"""
        queryset = Play.objects.all().prefetch_related("actors", "genres")
        title = self.request.query_params.get("title")
        genre = self.request.query_params.get("genre")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if genre:
            q = Q()
            for searched_genre in genre.split(","):
                q |= Q(genres__name__icontains=searched_genre)
            queryset = queryset.filter(q)

        return queryset.distinct()

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

    def get_queryset(self):
        queryset = Reservation.objects.all()
        if self.action == "list":
            queryset = queryset.filter(user__id=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PerformanceListRetrieveSerializer
        return PerformanceSerializer
