# Generated by Django 3.1.2 on 2020-10-11 14:38

from django.db import migrations, models
import django.db.models.deletion
import questions.models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_options_vote_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='content',
            field=models.CharField(max_length=250),
        ),
        migrations.CreateModel(
            name='QuestionMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=questions.models.file_upload_path)),
                ('file_type', models.CharField(blank=True, max_length=150, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionFiles', to='questions.question')),
            ],
            options={
                'verbose_name_plural': 'Question Medias',
            },
        ),
    ]