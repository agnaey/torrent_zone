# Generated by Django 5.1.2 on 2025-01-30 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_cart_price_cart_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='price',
            field=models.IntegerField(),
        ),
    ]
