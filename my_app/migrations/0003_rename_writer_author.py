# Generated by Django 5.0.6 on 2024-07-04 23:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_writer'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Writer',
            new_name='Author',
        ),
    ]
