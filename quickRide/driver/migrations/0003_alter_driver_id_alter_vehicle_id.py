# Generated by Django 5.0.6 on 2024-07-06 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
