from django.db import models
from users.models import User

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

    @property  # / Даниил
    def rating(self):
        """Рейтинг произведения"""
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        from django.db import models as django_models
        total = reviews.aggregate(total=django_models.Sum('score'))['total']
        return round(total / reviews.count())


class Review(models.Model):  # / Даниил
    """Отзыв на произведение"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveIntegerField(
        verbose_name='Рейтинг',
        help_text='Оценка от 1 до 10'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author_review',
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author.username} на {self.title.name}'


class Comment(models.Model):  # / Даниил
    """Комментарий к отзыву"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий {self.author.username} к отзыву {self.review.id}'
