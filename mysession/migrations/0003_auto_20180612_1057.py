# Generated by Django 2.0.5 on 2018-06-12 03:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysession', '0002_auto_20180612_1052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authuseravatar',
            name='user',
        ),
        migrations.AddField(
            model_name='authuserprofile',
            name='image_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='authuser',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 12, 10, 57, 28, 900050)),
        ),
        migrations.DeleteModel(
            name='AuthUserAvatar',
        ),
    ]
