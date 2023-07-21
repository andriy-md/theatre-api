from rest_framework import serializers

from theatre.models import Genre, Actor, Play


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
