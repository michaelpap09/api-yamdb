import csv
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction
from django.utils.dateparse import parse_datetime

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title

User = get_user_model()


class Command(BaseCommand):
    help = 'Imports demo data from CSV files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=Path,
            default=settings.BASE_DIR / 'static' / 'data',
            help='Directory containing CSV files.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.data_dir = options['data_dir'].resolve()
        if not self.data_dir.is_dir():
            raise CommandError(
                f'Data directory not found: {self.data_dir}'
            )

        loaders = (
            ('users.csv', self.load_users),
            ('category.csv', self.load_categories),
            ('genre.csv', self.load_genres),
            ('titles.csv', self.load_titles),
            ('genre_title.csv', self.load_title_genres),
            ('review.csv', self.load_reviews),
            ('comments.csv', self.load_comments),
        )

        for filename, loader in loaders:
            try:
                count = loader(filename)
            except (DatabaseError, KeyError, TypeError, ValueError) as error:
                raise CommandError(
                    f'Failed to import {filename}: {error}'
                ) from error
            self.stdout.write(f'{filename}: processed {count} rows')

        self.stdout.write(self.style.SUCCESS('CSV import completed.'))

    def read_rows(self, filename, required_fields):
        path = self.data_dir / filename
        if not path.is_file():
            raise CommandError(f'File not found: {path}')

        with path.open(encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            missing = set(required_fields) - set(reader.fieldnames or ())
            if missing:
                fields = ', '.join(sorted(missing))
                raise CommandError(
                    f'{filename} is missing columns: {fields}'
                )
            yield from enumerate(reader, start=2)

    def load_users(self, filename):
        fields = (
            'id', 'username', 'email', 'role', 'bio', 'first_name',
            'last_name',
        )
        count = 0
        for line_number, row in self.read_rows(filename, fields):
            try:
                user, created = User.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        'bio': row['bio'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                    },
                )
                if created:
                    user.set_unusable_password()
                    user.save(update_fields=('password',))
            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)
            count += 1
        return count

    def load_categories(self, filename):
        return self.load_named_models(filename, Category)

    def load_genres(self, filename):
        return self.load_named_models(filename, Genre)

    def load_named_models(self, filename, model):
        count = 0
        for line_number, row in self.read_rows(
            filename,
            ('id', 'name', 'slug'),
        ):
            try:
                model.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    },
                )
            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)
            count += 1
        return count

    def load_titles(self, filename):
        count = 0
        for line_number, row in self.read_rows(
            filename,
            ('id', 'name', 'year', 'category'),
        ):
            try:
                Title.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'year': int(row['year']),
                        'category_id': int(row['category']),
                    },
                )
            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)
            count += 1
        return count

    def load_title_genres(self, filename):
        through_model = Title.genre.through
        count = 0
        for line_number, row in self.read_rows(
            filename,
            ('id', 'title_id', 'genre_id'),
        ):
            try:
                through_model.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'title_id': int(row['title_id']),
                        'genre_id': int(row['genre_id']),
                    },
                )
            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)
            count += 1
        return count

    def load_reviews(self, filename):
        fields = ('id', 'title_id', 'text', 'author', 'score', 'pub_date')
        count = 0
        for line_number, row in self.read_rows(filename, fields):
            try:
                review, _ = Review.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'title_id': int(row['title_id']),
                        'text': row['text'],
                        'author_id': int(row['author']),
                        'score': int(row['score']),
                    },
                )
                Review.objects.filter(pk=review.pk).update(
                    created_at=self.parse_date(row['pub_date']),
                )
            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)
            count += 1
        return count

    def load_comments(self, filename):
        fields = ('id', 'review_id', 'text', 'author', 'pub_date')
        count = 0
        for line_number, row in self.read_rows(filename, fields):
            try:
                comment, _ = Comment.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'review_id': int(row['review_id']),
                        'text': row['text'],
                        'author_id': int(row['author']),
                    },
                )
                Comment.objects.filter(pk=comment.pk).update(
                    created_at=self.parse_date(row['pub_date']),
                )
            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)
            count += 1
        return count

    @staticmethod
    def parse_date(value):
        parsed = parse_datetime(value)
        if parsed is None:
            raise ValueError(f'invalid date: {value}')
        return parsed

    @staticmethod
    def raise_row_error(filename, line_number, error):
        raise CommandError(
            f'{filename}, line {line_number}: {error}'
        ) from error
