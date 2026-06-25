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


IMPORT_CONFIG = (
    {
        'filename': 'users.csv',
        'model': User,
        'fields': (
            'id', 'username', 'email', 'role',
            'bio', 'first_name', 'last_name',
        ),
        'int_fields': ('id',),
    },
    {
        'filename': 'category.csv',
        'model': Category,
        'fields': ('id', 'name', 'slug'),
        'int_fields': ('id',),
    },
    {
        'filename': 'genre.csv',
        'model': Genre,
        'fields': ('id', 'name', 'slug'),
        'int_fields': ('id',),
    },
    {
        'filename': 'titles.csv',
        'model': Title,
        'fields': ('id', 'name', 'year', 'category'),
        'int_fields': ('id', 'year', 'category'),
        'rename_fields': {'category': 'category_id'},
    },
    {
        'filename': 'genre_title.csv',
        'model_getter': lambda: Title.genre.through,
        'fields': ('id', 'title_id', 'genre_id'),
        'int_fields': ('id', 'title_id', 'genre_id'),
    },
    {
        'filename': 'review.csv',
        'model': Review,
        'fields': ('id', 'title_id', 'text', 'author', 'score', 'pub_date'),
        'int_fields': ('id', 'title_id', 'author', 'score'),
        'rename_fields': {'author': 'author_id'},
        'date_field': 'created_at',
        'csv_date_field': 'pub_date',
    },
    {
        'filename': 'comments.csv',
        'model': Comment,
        'fields': ('id', 'review_id', 'text', 'author', 'pub_date'),
        'int_fields': ('id', 'review_id', 'author'),
        'rename_fields': {'author': 'author_id'},
        'date_field': 'created_at',
        'csv_date_field': 'pub_date',
    },
)


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
            raise CommandError(f'Data directory not found: {self.data_dir}')

        for config in IMPORT_CONFIG:
            filename = config['filename']
            try:
                count = self.load_model_data(config)
            except (DatabaseError, KeyError, TypeError, ValueError) as error:
                raise CommandError(
                    f'Failed to import {filename}: {error}'
                ) from error

            self.stdout.write(f'{filename}: processed {count} rows')

        self.stdout.write(self.style.SUCCESS('CSV import completed.'))

    def load_model_data(self, config):
        filename = config['filename']
        model = config.get('model') or config['model_getter']()
        fields = config['fields']

        count = 0

        for line_number, row in self.read_rows(filename, fields):
            try:
                data = self.prepare_row(row, config)

                obj, created = model.objects.update_or_create(
                    id=data.pop('id'),
                    defaults=data,
                )

                if model is User and created:
                    obj.set_unusable_password()
                    obj.save(update_fields=('password',))

                if 'date_field' in config:
                    model.objects.filter(pk=obj.pk).update(
                        **{
                            config['date_field']: self.parse_date(
                                row[config['csv_date_field']]
                            )
                        }
                    )

            except (DatabaseError, TypeError, ValueError) as error:
                self.raise_row_error(filename, line_number, error)

            count += 1

        return count

    def prepare_row(self, row, config):
        rename_fields = config.get('rename_fields', {})
        int_fields = config.get('int_fields', ())
        skip_fields = {config.get('csv_date_field')}

        data = {}

        for field in config['fields']:
            if field in skip_fields:
                continue

            value = row[field]

            if field in int_fields:
                value = int(value)

            model_field = rename_fields.get(field, field)
            data[model_field] = value

        return data

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
