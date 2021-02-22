# Generated by Django 3.1.2 on 2020-10-09 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answers', '0002_auto_20201009_0105'),
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('normal', 'Normal'), ('poll', 'Poll')], default='Normal', max_length=10),
        ),
        migrations.DeleteModel(
            name='PollQuestion',
        ),
    ]