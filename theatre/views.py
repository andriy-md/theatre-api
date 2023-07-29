from django.db.models import Q
from rest_framework import viewsets, views, status

from theatre.models import Genre, Actor, Play, TheatreHall, Reservation, Performance, Ticket
from theatre.serializers import GenreSerializer, ActorSerializer, PlaySerializer, PlayListRetrieveSerializer, \
    TheatreHallSerializer, ReservationSerializer, PerformanceSerializer, PerformanceListRetrieveSerializer, \
    TicketSerializer, TicketListRetrieveSerializer


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class ActorViewSet(viewsets.ModelViewSet):
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all().prefetch_related("actors", "genres")

    def get_queryset(self):
        """Search plays"""
        queryset = Play.objects.all().prefetch_related("actors", "genres")
        title = self.request.query_params.get("title")
        genre = self.request.query_params.get("genre")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if genre:
            searched_genres = genre.split(",")
            q = Q()
            for searched_genre in searched_genres:
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


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PerformanceListRetrieveSerializer
        return PerformanceSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related("performance", "reservation")
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TicketListRetrieveSerializer
        return TicketSerializer
