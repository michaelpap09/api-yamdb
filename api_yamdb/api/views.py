from django.shortcuts import render
from rest_framework import viewsets

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
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = ()

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete(author=self.request.user)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = ()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = ()


class ReviewViewSet(viewsets.ModelViewSet):
    pass  # Для Даниила


class CommentViewSet(viewsets.ModelViewSet):
    pass  # Для Даниила


class UserViewSet(viewsets.ModelViewSet):
    pass  # Для Антона