from django.db import models

class Cooking_data(models.Model):
    # id = models.IntegerField(primary_key=True) #ID
    name = models.CharField(max_length=100)  # 料理名
    image_path = models.ImageField(upload_to='cooking_images/')  # 画像のパス
    red = models.IntegerField()  # RGB値
    green = models.IntegerField()
    blue = models.IntegerField()
    size_category = models.CharField(max_length=50)  # サイズカテゴリ

    initial_red = models.IntegerField(default=0)
    initial_green = models.IntegerField(default=0)
    initial_blue = models.IntegerField(default=0)

    def __str__(self):
        return self.name
