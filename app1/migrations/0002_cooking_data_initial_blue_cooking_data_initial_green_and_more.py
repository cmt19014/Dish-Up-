# Generated by Django 5.0 on 2024-01-08 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cooking_data',
            name='initial_blue',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cooking_data',
            name='initial_green',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cooking_data',
            name='initial_red',
            field=models.IntegerField(default=0),
        ),
    ]
