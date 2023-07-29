from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from theatre.models import Genre, Actor, Play, TheatreHall, Reservation, Performance, Ticket


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", "first_name", "last_name"]


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ["title", "description", "actors", "genres"]


class PlayListRetrieveSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    actors = serializers.SlugRelatedField(many=True, slug_field="full_name", read_only=True)

    class Meta:
        model = Play
        fields = ["title", "description", "actors", "genres"]


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ["id", "name", "rows", "seats_in_row", "capacity"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "created_at", "user"]


class PerformanceListRetrieveSerializer(serializers.ModelSerializer):
    play = serializers.SlugRelatedField(slug_field="title", read_only=True)
    theatre_hall = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Performance
        fields = ["id", "play", "theatre_hall", "show_time"]


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ["id", "play", "theatre_hall", "show_time"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation"]
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("row", "seat", "performance"),
                message="This seat has already been taken"
            )
        ]

    def get_related_performance_object(self):
        return Performance.objects.get(id=self.initial_data["performance"])

    def validate_row(self, value):
        performance = self.get_related_performance_object()
        if not (1 <= value <= performance.theatre_hall.rows):
            raise ValidationError(f"Row must be in range 1-{performance.theatre_hall.rows}")
        return value

    def validate_seat(self, value):
        performance = self.get_related_performance_object()
        if not (1 <= value <= performance.theatre_hall.seats_in_row):
            raise ValidationError(f"Seat must be in range 1-{performance.theatre_hall.seats_in_row}")
        return value



class TicketListRetrieveSerializer(serializers.ModelSerializer):
    performance = PerformanceListRetrieveSerializer()

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation"]
