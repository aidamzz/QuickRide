# Generated by Django 5.0.6 on 2024-07-07 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_trip_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='destination_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='origin_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
