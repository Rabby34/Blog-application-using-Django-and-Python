# Generated by Django 5.1.4 on 2024-12-09 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_subscribe'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]