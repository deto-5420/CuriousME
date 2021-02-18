# Generated by Django 3.1.2 on 2020-10-11 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questions', '0008_remove_question_files'),
        ('accounts', '0005_auto_20201011_0738'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change', models.CharField(max_length=250)),
                ('rtype', models.CharField(choices=[('post', 'Post'), ('edit', 'Edit'), ('delete', 'Delete')], max_length=10)),
                ('approved', models.BooleanField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
            ],
        ),
        migrations.CreateModel(
            name='OptionChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change', models.CharField(max_length=250)),
                ('rtype', models.CharField(choices=[('post', 'Post'), ('edit', 'Edit'), ('delete', 'Delete')], max_length=10)),
                ('approved', models.BooleanField(default=0)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.options')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
            ],
        ),
    ]
