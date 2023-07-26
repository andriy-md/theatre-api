from rest_framework import serializers

from theatre.models import Genre, Actor, Play, TheatreHall, Reservation, Performance


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["first_name", "last_name"]


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
