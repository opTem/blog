# Generated by Django 2.2.7 on 2019-11-27 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='new',
            field=models.IntegerField(default=0),
        ),
    ]
