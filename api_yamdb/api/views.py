from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import models

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


class CommentViewSet(viewsets.ModelViewSet):  # / Даниил
    """ViewSet для комментариев"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrAuthenticated]

    def get_queryset(self):
        review_id = self.context.get('review_id')
        if review_id:
            return Comment.objects.filter(review_id=review_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = ()


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):  # / Даниил
    """ViewSet для отзывов"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrAuthenticated]

    def get_queryset(self):
        title_id = self.context.get('title_id')
        if title_id:
            return Review.objects.filter(title_id=title_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save(author=self.request.user)
        return instance

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
