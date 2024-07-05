import csv

from django.core.management import BaseCommand

from recipes.models import (Ingredient, Tag)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'slug': 'breakfast'},
            {'name': 'Обед', 'slug': 'lunch'},
            {'name': 'Ужин', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        with open(
            '/data/ingridients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in csv.DictReader(file))
