from datetime import date

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from titles.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        write_only=True,
    )
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
        write_only=True,
        allow_empty=False,
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre',
            'category'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['description'] = data['description'] or ''
        data['category'] = CategorySerializer(instance.category).data
        data['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        return data

    def validate_year(self, value):
        if value > date.today().year:
            raise serializers.ValidationError(
                'The release year cannot be in the future.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    pub_date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date', 'review')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    score = serializers.IntegerField(min_value=1, max_value=10)
    pub_date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'pub_date')

    def validate(self, data):
        if self.instance is None:
            title = self.context.get('title')
            author = self.context['request'].user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Only one review per title is allowed.'
                )
        return data
