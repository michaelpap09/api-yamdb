from django.db import models

MAX_LENGTH = 255


class Category(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название',
    )
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        'Genre',
        related_name='titles',
        verbose_name='Жанры',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name

    @property
    def rating(self):
        """Рейтинг произведения"""
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        average = reviews.aggregate(value=models.Avg('score'))['value']
        return round(average)
