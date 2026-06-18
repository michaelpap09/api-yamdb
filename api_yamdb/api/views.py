from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        if review_id:
            return Comment.objects.filter(review_id=review_id)
        return Comment.objects.all()

    def create(self, request, *args, **kwargs):
        """Создание комментария"""
        review_id = self.kwargs.get('review_id')
        if not review_id:
            return Response(
                {'detail': 'Отзыв не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        review = get_object_or_404(Review, id=review_id)
        data = request.data.copy()
        data['review'] = review.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Получение комментария по ID"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Обновление комментария"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление комментария"""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """Права доступа для комментариев"""
        if self.action in ['create']:
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
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        title_id = self.request.query_params.get('title_id')
        if title_id:
            return Review.objects.filter(title_id=title_id)
        return Review.objects.all()

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        if title_id:
            return get_object_or_404(Title, id=title_id)
        return None

    def create(self, request, *args, **kwargs):
        """Создание отзыва"""
        title = self.get_title()
        if not title:
            return Response(
                {'detail': 'Произведение не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        data = request.data.copy()
        data['title'] = title.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Получение отзыва по ID"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Обновление отзыва"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление отзыва"""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """Права доступа для отзывов"""
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
