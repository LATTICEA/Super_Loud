# Generated by Django 3.2 on 2022-03-25 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription_details',
            name='cancel_at',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='subscription_details',
            name='canceled_at',
            field=models.DateField(null=True),
        ),
    ]
