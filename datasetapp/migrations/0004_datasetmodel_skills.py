# Generated by Django 3.2 on 2022-10-25 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasetapp', '0003_auto_20220902_0301'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetmodel',
            name='skills',
            field=models.CharField(default=' ', max_length=1),
        ),
    ]
