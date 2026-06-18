from rest_framework import serializers

from titles.models import (
    Title,
    Comment,
    Review,
    Category,
    Genre
)


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):  # / Даниил
        """Получение рейтинга произведения"""
        reviews = obj.reviews.all()
        if not reviews.exists():
            return None
        total = reviews.aggregate(total=serializers.Sum('score'))['total']
        return round(total / reviews.count())


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):  # / Даниил
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'created_at', 'review']
        read_only_fields = ['author', 'created_at', 'review']


class ReviewSerializer(serializers.ModelSerializer):  # / Даниил
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField()

    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'created_at', 'title']
        read_only_fields = ['author', 'created_at']

    def validate(self, data):
        """Проверка: на одно произведение только один отзыв от пользователя"""
        if self.instance is None:
            title = data.get('title')
            author = self.context['request'].user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'На одно произведение можно оставить только один отзыв'
                )
        return data

    def validate_score(self, value):
        """Проверка диапазона оценки от 1 до 10"""
        if value < 1 or value > 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')
        return value
