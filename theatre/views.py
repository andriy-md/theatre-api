from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from theatre.models import Genre, Actor, Play, TheatreHall, Reservation, Performance
from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    PlayListRetrieveSerializer,
    TheatreHallSerializer,
    ReservationSerializer,
    PerformanceSerializer,
    PerformanceListRetrieveSerializer,
    ReservationListSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class ActorViewSet(viewsets.ModelViewSet):
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all().prefetch_related("actors", "genres")
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    pagination_class = PageNumberPagination

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

    @extend_schema(
        parameters=[
            OpenApiParameter("title", description="Filter by title", type=str),
            OpenApiParameter(
                "genre",
                description="Filter by genre",
                type={"type": "list", "items": {"type": "str"}},
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PerformanceListRetrieveSerializer
        return PerformanceSerializer
