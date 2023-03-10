# Generated by Django 3.1.4 on 2021-12-29 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='subscription_details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodtype', models.CharField(choices=[('Monthly', 'Monthly'), ('Annually', 'Annually'), ('Trial', 'Trial')], max_length=20)),
                ('subtype', models.CharField(choices=[('Data', 'Data'), ('Data+Predictions', 'Data+Predictions')], max_length=20)),
                ('start_date', models.DateField(null=True)),
                ('next_date', models.DateField(null=True)),
                ('trial_availed', models.BooleanField(default=False)),
                ('amount_paid', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=False)),
                ('stripeCustomerId', models.CharField(max_length=255, null=True)),
                ('stripeSubscriptionId', models.CharField(max_length=255, null=True)),
                ('userpoolobj', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.userpool')),
            ],
        ),
    ]
