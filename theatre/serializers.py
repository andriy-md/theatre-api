from django.db import transaction
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
        fields = ["row", "seat", "performance"]
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("row", "seat", "performance"),
                message="This seat has already been taken"
            )
        ]

    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["performance"],
            ValidationError
        )
        return data


class TicketListRetrieveSerializer(serializers.ModelSerializer):
    performance = PerformanceListRetrieveSerializer()

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation"]


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(read_only=False, many=True, allow_null=False)

    class Meta:
        model = Reservation
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket in tickets:
                Ticket.objects.create(reservation=reservation, **ticket)
            return reservation


class ReservationListSerializer(serializers.ModelSerializer):
    tickets = TicketListRetrieveSerializer(many=True, read_only=True)
