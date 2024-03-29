# Generated by Django 3.1 on 2020-09-01 08:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ecommerce', '0007_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=10)),
                ('total_amount', models.FloatField(default=0)),
                ('coupon', models.CharField(blank=True, max_length=10, null=True)),
                ('coupon_amount', models.FloatField(default=0)),
                ('order_amount', models.FloatField(default=0)),
                ('savings', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecommerce.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
