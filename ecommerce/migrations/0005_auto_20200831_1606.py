# Generated by Django 3.1 on 2020-08-31 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0004_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.IntegerField(),
        ),
    ]