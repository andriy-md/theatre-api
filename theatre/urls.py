from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    GenreViewSet,
    ActorViewSet,
    PlayViewSet,
    TheatreHallViewSet,
    ReservationViewSet,
    PerformanceViewSet,
)

router = routers.DefaultRouter()

router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("plays", PlayViewSet)
router.register("theatre-halls", TheatreHallViewSet)
router.register("reservations", ReservationViewSet)
router.register("performances", PerformanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "theatre"
