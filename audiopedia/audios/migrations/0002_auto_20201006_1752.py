# Generated by Django 2.1.4 on 2020-10-06 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='duration',
            field=models.IntegerField(),
        ),
    ]
