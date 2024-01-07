import pandas as pd
from django.core.management.base import BaseCommand
from app1.models import Cooking_data

class Command(BaseCommand):
    help = 'Import cooking data from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            Cooking_data.objects.create(
                # id=row['ID'],  #id is automatically assigned by Django 
                name=row['料理名'],
                image_path=row['画像パス'],
                red=row['R'],
                green=row['G'],
                blue=row['B'],
                size_category=row['サイズ']
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported dishes'))
