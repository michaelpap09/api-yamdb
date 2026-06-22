from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets

from reviews.models import Review
from titles.models import Category, Genre, Title
from users.permissions import (
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_queryset(self):
        queryset = Title.objects.all()
        genre = self.request.query_params.get('genre')
        category = self.request.query_params.get('category')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')

        if genre:
            queryset = queryset.filter(genre__slug=genre)
        if category:
            queryset = queryset.filter(category__slug=category)
        if year:
            queryset = queryset.filter(year=year)
        if name:
            queryset = queryset.filter(name=name)
        return queryset.distinct()


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_pk'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs.get('rev_pk'),
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = self.get_title()
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('rev_pk'),
            title_id=self.kwargs.get('title_pk'),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs.get('com_pk'),
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
