from django.db import models

MAX_LENGTH = 255


class Category(models.Model):
    name = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    pass  # Для Даниила 


class Comment(models.Model):
    pass  # Для Даниила


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )
    genre = models.ManyToManyField('Genre', related_name='titles')

    def __str__(self):
        return self.name