from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from titles.models import (
    Title,
    Comment,
    Review,
    Category,
    Genre
)


class TitleSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__' 


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        pass  # Для Даниила


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        pass  # Для Даниила