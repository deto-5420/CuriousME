# Generated by Django 3.1.2 on 2020-10-29 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20201028_2320'),
        ('replies', '0005_auto_20201011_0814'),
        ('adminpanel', '0002_spammedanswer_spammedquestion_spammereply'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SpammeReply',
            new_name='SpammedReply',
        ),
        migrations.RemoveField(
            model_name='questionchangerequest',
            name='question',
        ),
        migrations.RemoveField(
            model_name='questionchangerequest',
            name='user',
        ),
        migrations.DeleteModel(
            name='OptionChangeRequest',
        ),
        migrations.DeleteModel(
            name='QuestionChangeRequest',
        ),
    ]