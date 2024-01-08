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
            # 料理データの作成
            dish, created = Cooking_data.objects.get_or_create(
                name=row['料理名'],
                image_path=row['画像パス'],
                red=row['R'],
                green=row['G'],
                blue=row['B'],
                size_category=row['サイズ']
            )

            # 初期値を設定（すでに存在する場合は更新しない）
            if created:
                dish.initial_red = row['R']
                dish.initial_green = row['G']
                dish.initial_blue = row['B']
                dish.save()

        self.stdout.write(self.style.SUCCESS('Successfully imported dishes'))
