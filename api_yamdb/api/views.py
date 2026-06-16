from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from titles.models import (
    Title,
    Comment,
    Review,
    Category,
    Genre
)
from .serializers import (
    TitleSerializer,
    CommentSerializer,
    ReviewSerializer,
    CategorySerializer,
    GenreSerializer
)


class TitleViewSet(viewsets.ModelViewSet):
    pass


class CommentViewSet(viewsets.ModelViewSet):
    pass


class GenreViewSet(viewsets.ModelViewSet):
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    pass