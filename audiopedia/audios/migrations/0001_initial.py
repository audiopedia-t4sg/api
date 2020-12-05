# Generated by Django 3.1.2 on 2020-12-05 19:59

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the language.', max_length=100)),
                ('audio_url', models.URLField(help_text='URL of audios.')),
                ('published', models.BooleanField(default=True, help_text='Decide whether this language is ready for users to see.')),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='The title of the playlist.', max_length=200)),
                ('index', models.IntegerField(help_text='The position of the playlist within a topic.')),
                ('audio_url', models.URLField(help_text='URL to the audio directory associated with the playlist.')),
                ('active', models.BooleanField(default=True, help_text='Inactivate to temporarily delete playlist and reactivate to recover.')),
                ('published', models.BooleanField(default=True, help_text='Decide to show or hide the playlist from the users.')),
                ('language', models.ForeignKey(help_text='The language of the track.', on_delete=django.db.models.deletion.CASCADE, to='audios.language')),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the track.', max_length=200)),
                ('index', models.IntegerField(help_text='The position of the track within a playlist.')),
                ('audio_url', models.URLField(help_text='URL to the audio file that goes with this track.')),
                ('transcript', models.TextField(help_text='A string/text transcript that goes along with the audio.')),
                ('duration', models.IntegerField(help_text='Duration in seconds.')),
                ('created_at', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='When the track was created.')),
                ('updated_at', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='When the track was last updated.')),
                ('active', models.BooleanField(default=True, help_text='Inactivate to temporarily delete track and reactivate to recover.')),
                ('published', models.BooleanField(default=True, help_text='Decide whether this track is ready for users to see.')),
                ('language', models.ForeignKey(help_text='The language of the track.', on_delete=django.db.models.deletion.CASCADE, to='audios.language')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='The name of the topic.', max_length=200)),
                ('index', models.IntegerField(help_text='The order/position of the topic within the interface.')),
                ('audio_url', models.URLField(help_text='URL to the audio directory associated with the topic.')),
                ('active', models.BooleanField(default=True, help_text='Inactivate to temporarily delete topic and reactivate to recover.')),
                ('published', models.BooleanField(default=True, help_text='Decide to show or hide the topic from the users.')),
                ('language', models.ForeignKey(help_text='The language of the track.', on_delete=django.db.models.deletion.CASCADE, to='audios.language')),
                ('playlists', models.ManyToManyField(help_text='A list of all the playlists this topic contains.', to='audios.Playlist')),
            ],
        ),
        migrations.AddField(
            model_name='playlist',
            name='tracks',
            field=models.ManyToManyField(help_text='A list of all the tracks this playlist contains.', to='audios.Track'),
        ),
    ]
