from datetime import date

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title

MIN_SCORE = 1
MAX_SCORE = 10


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
                'Год выпуска не может быть в будущем.'
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
    score = serializers.IntegerField(min_value=MIN_SCORE, max_value=MAX_SCORE)
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
                    'Только один отзыв разрешен.'
                )
        return data
