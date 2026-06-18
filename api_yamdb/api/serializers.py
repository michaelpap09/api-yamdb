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
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
        read_only_fields = ['author', 'pub_date', 'review']


class ReviewSerializer(serializers.ModelSerializer):  # / Даниил
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(min_value=1, max_value=10)
    pub_date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        read_only_fields = ['author', 'pub_date']

    def validate(self, data):
        """Проверка: на одно произведение только один отзыв от пользователя"""
        if self.instance is None:
            title_id = self.context.get('title_id')
            if title_id:
                title = Title.objects.get(id=title_id)
                author = self.context['request'].user
                if Review.objects.filter(title=title, author=author).exists():
                    raise serializers.ValidationError(
                        'На одно произведение можно оставить только один отзыв'
                    )
        return data
