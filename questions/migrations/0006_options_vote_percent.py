# Generated by Django 3.1.2 on 2020-10-10 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_auto_20201009_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='options',
            name='vote_percent',
            field=models.FloatField(default=0),
        ),
    ]