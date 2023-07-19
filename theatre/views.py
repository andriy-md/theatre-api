from django.shortcuts import render
from rest_framework import viewsets

from theatre.models import Genre
from theatre.serializers import GenreSerializer


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
