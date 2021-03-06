import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
import graphql_jwt
from graphql_relay import from_global_id
from graphene import relay, ObjectType
from .models import Language, Track, Playlist, Topic

def check_logged_in(info):
    user = info.context.user
    if user.is_anonymous:
        raise Exception('User not authenticated')
    return user

class LanguageType(DjangoObjectType):
    class Meta:
        model = Language
        filter_fields = ("id", "name", "audio_url", "published")
        interfaces = (relay.Node, )

class TrackType(DjangoObjectType):
    class Meta:
        model = Track
        filter_fields = ("id", "title", "index", "audio_url", "transcript", "duration", "created_at", "updated_at", "active", "published", "language_id")
        interfaces = (relay.Node, )

class PlaylistType(DjangoObjectType):
    
    # get tracks by playlist workaround?
    # tracks = graphene.List(TrackType)

    # @graphene.resolve_only_args
    # def resolve_tracks(self):
    #     return self.tracks.all()

    class Meta:
        model = Playlist
        filter_fields = ("id", "title", "index", "audio_url", "active", "published", "tracks", "language_id")
        interfaces = (relay.Node, )

class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        filter_fields=("id", "title", "index", "audio_url", "active", "published", "playlists", "language_id")
        interfaces = (relay.Node, )

class LanguageInput(graphene.InputObjectType):
    name = graphene.String(description="Name of the language")
    audio_url = graphene.String(description="URL to audio directory associated with the language")
    published = graphene.Boolean(description="Visible to user if true")

class TrackInput(graphene.InputObjectType):
    index = graphene.ID(description="Position of the track within a playlist")
    title = graphene.String(description="Title of the track")
    audio_url = graphene.String(description="URL to the audio file associated with this track")
    transcript = graphene.String(description="Transcript that goes along with this track")
    duration = graphene.Int(description="Duration of the track in seconds")
    active = graphene.Boolean(description="Inactivate to temporarily delete track and reactivate to recover")
    published = graphene.Boolean(description="Visible to user if true")
    language_id = graphene.ID(description="ID of the language object")
    playlist = graphene.ID(description="ID of playlist that this track belongs to")
    
class PlaylistInput(graphene.InputObjectType):
    index = graphene.ID(description="Position of the playlist within a topic")
    title = graphene.String(description="Title of the playlist")
    audio_url = graphene.String(description="URL to the audio directory associated with this playlist")
    active = graphene.Boolean(description="Inactivate to temporarily delete playlist and reactivate to recover")
    published = graphene.Boolean(description="Visible to user if true")
    language_id = graphene.ID(description="ID of the language object")
    topic = graphene.ID(description="ID of topic that this track belongs to")

class TopicInput(graphene.InputObjectType):
    index = graphene.ID(description="Position/placement of the topic among a list of topics")
    title = graphene.String(description="Title of the topic")
    audio_url = graphene.String(description="URL to the audio directory associated with this topic")
    active = graphene.Boolean(description="Inactivate to temporarily delete topic and reactivate to recover")
    published = graphene.Boolean(description="Visible to user if true")
    language_id = graphene.ID(description="ID of the language object")

class CreateLanguage(graphene.Mutation):
    class Arguments:
        input = LanguageInput(required=True, description="Look at LanguageInput definition for more details")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    language = graphene.Field(LanguageType)

    @staticmethod
    def mutate(root, info, input=None):
        user = check_logged_in(info)
        if user:
            ok = True
            lang_instance = Language(
                name = input.name,
                audio_url = input.audio_url,
                published = input.published,
                )
            lang_instance.save()
            return CreateLanguage(ok=ok, language=lang_instance, user=user)

class UpdateLanguage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the language to be updated")
        name = graphene.String(description="New name for the language")
        audio_url = graphene.String(description="New URL")
        published = graphene.Boolean(description="Update published status")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    language = graphene.Field(LanguageType)

    @staticmethod
    def mutate(root, info, id, name=None, published=None, audio_url=None):
        user = check_logged_in(info)
        if user:
            ok = False
            lang_instance = Language.objects.get(pk=from_global_id(id)[1])
            if lang_instance:
                ok = True
                if audio_url:
                    lang_instance.audio_url = audio_url
                if name:
                    lang_instance.transcript = name
                if published != None:
                    lang_instance.published = published

                lang_instance.save()
                return UpdateLanguage(ok=ok, language=lang_instance, user=user)
            return UpdateLanguage(ok=ok, language=None, user=user)

class DeleteLanguage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the language to be deleted")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")

    @staticmethod
    def mutate(root, info, id):
        user = check_logged_in(info)
        if user:
            obj = Language.objects.get(pk=from_global_id(id)[1])
            obj.delete()
            return DeleteLanguage(ok=True, user=user)

class CreateTopic(graphene.Mutation):
    class Arguments:
        input = TopicInput(required=True, description="Look at TopicInput definition for more details")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    topic = graphene.Field(TopicType)

    @staticmethod
    def mutate(root, info, input=None):
        user = check_logged_in(info)
        if user:
            ok = True
            topic_instance = Topic(
                index = input.index,
                title=input.title,
                audio_url = input.audio_url,
                active = input.active,
                published = input.published,
                language_id = from_global_id(input.language_id)[1]
                )
            topic_instance.save()
            return CreateTopic(ok=ok, topic=topic_instance, user=user)
        
class UpdateTopic(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the topic to be updated")
        index = graphene.Int(description="New position of the topic among a list of topics")
        title = graphene.String(description="New title for the topic")
        audio_url = graphene.String(description="New URL")
        active = graphene.Boolean(description="Updated active status")
        published = graphene.Boolean(description="Updated published status")
        language_id = graphene.ID(description="ID of the language object")

    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    topic = graphene.Field(TopicType)

    @staticmethod
    def mutate(root, info, id, index=None, active=None, published=None, playlists=[], title=None, audio_url=None):
        user = check_logged_in(info)
        if user:
            ok = False
            topic_instance = Topic.objects.get(pk=from_global_id(id)[1])
            if topic_instance:
                ok = True
                if index: topic_instance.index = index
                if title: topic_instance.title = title
                if audio_url: topic_instance.audio_url = audio_url
                if active != None: topic_instance.active = active
                if published != None: topic_instance.published = published

                topic_instance.save()
                return UpdateTopic(ok=ok, topic=topic_instance, user=user)
            return UpdateTopic(ok=ok, topic=None, user=user)

class DeleteTopic(graphene.Mutation):
    class Arguments:
        id = graphene.ID(description="ID of the topic to be deleted")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")

    @staticmethod
    def mutate(root, info, id):
        user = check_logged_in(info)
        if user:
            obj = Topic.objects.get(pk=from_global_id(id)[1])
            obj.delete()
            return DeleteTopic(ok=True, user=user)


class CreatePlaylist(graphene.Mutation):
    class Arguments:
        input = PlaylistInput(required=True, description="Look at PlaylistInput definition for more details")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    playlist = graphene.Field(PlaylistType)

    @staticmethod
    def mutate(root, info, input=None):
        user = check_logged_in(info)
        if user:    
            ok = True
            playlist_instance = Playlist(
                index = input.index,
                title=input.title,
                audio_url = input.audio_url,
                active = input.active,
                published = input.published,
                language_id = from_global_id(input.language_id)[1]
                )
            playlist_instance.save()

            if input.topic:
                topic = Topic.objects.get(pk=from_global_id(input.topic)[1])
                topic.playlists.add(playlist_instance)
            
            return CreatePlaylist(ok=ok, playlist=playlist_instance, user=user)
        
class UpdatePlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the playlist to be updated")
        index = graphene.Int(description="New position of the playlist within a topic")
        title = graphene.String(description="New title")
        audio_url = graphene.String(description="New URL")
        active = graphene.Boolean(description="New active status")
        published = graphene.Boolean(description="New upblished status")
        topic = graphene.ID(description="ID of the new topic object that this playlist belongs to")
        
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    playlist = graphene.Field(PlaylistType)

    @staticmethod
    def mutate(root, info, id, index=None, active=None, published=None, tracks=[], title=None, audio_url=None, topic=None):
        user = check_logged_in(info)
        if user:
            ok = False
            playlist_instance = Playlist.objects.get(pk=from_global_id(id)[1])
            if playlist_instance:
                ok = True
                if index: playlist_instance.index = index
                if title: playlist_instance.title = title
                if audio_url: playlist_instance.audio_url = audio_url
                if active != None: playlist_instance.active = active
                if published != None: playlist_instance.published = published
                
                if topic != None:
                    # Change playlist
                    old_topic = Topic.objects.get(playlists=from_global_id(id)[1])
                    new_topic = Topic.objects.get(pk=from_global_id(topic)[1])
                    old_topic.tracks.remove(playlist_instance)
                    new_topic.tracks.add(playlist_instance)

                playlist_instance.save()

                return UpdatePlaylist(ok=ok, playlist=playlist_instance, user=user)
            return UpdatePlaylist(ok=ok, playlist=None, user=user)

class DeletePlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.ID(description="ID of playlist to be deleted")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")

    @staticmethod
    def mutate(root, info, id):
        user = check_logged_in(info)
        if user:
            obj = Playlist.objects.get(pk=from_global_id(id)[1])
            obj.delete()
            return DeletePlaylist(ok=True, user=user)

class CreateTrack(graphene.Mutation):
    class Arguments:
        input = TrackInput(required=True, description="Look at TrackInput definition for more details")
    
    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")
    track = graphene.Field(TrackType)

    @staticmethod
    def mutate(root, info, input=None):
        user = check_logged_in(info)
        if user:
            ok = True
            track_instance = Track(
                index =input.index,
                title=input.title,
                audio_url = input.audio_url,
                transcript = input.transcript,
                duration = input.duration,
                created_at = timezone.now(),
                updated_at = timezone.now(),
                active = input.active,
                published = input.published,
                language_id = from_global_id(input.language_id)[1]
                )
            track_instance.save()

            # Add to playlist
            if input.playlist:
                playlist = Playlist.objects.get(pk=from_global_id(input.playlist)[1])
                playlist.tracks.add(track_instance)
            
            return CreateTrack(ok=ok, track=track_instance, user=user)

class UpdateTrack(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of track to be updated")
        index = graphene.Int(description="New position of the track within a playlist")
        transcript = graphene.String(description="New transcript")
        audio_url = graphene.String(description="New URL")
        duration = graphene.String(description="New duration")
        active = graphene.Boolean(description="New active status")
        published = graphene.Boolean(description="New published status")
        playlist = graphene.ID(description="ID of playlist that this track belongs")
        
    ok = graphene.Boolean()
    track = graphene.Field(TrackType)
    user = graphene.String(description="Username of the authenticated user")

    @staticmethod
    def mutate(root, info, id, index=None, active=None, published=None, duration=None, transcript=None, audio_url=None, playlist=None):
        user = check_logged_in(info)
        if user:
            ok = False
            track_instance = Track.objects.get(pk=from_global_id(id)[1])
            if track_instance:
                ok = True
                if index:
                    track_instance.index = index
                if audio_url:
                    track_instance.audio_url = audio_url
                if transcript:
                    track_instance.transcript = transcript
                if duration:
                    track_instance.duration = duration
                if active != None:
                    track_instance.active = active
                if published != None:
                    track_instance.published = published
                if playlist != None:
                    # Change playlist
                    old_playlist = Playlist.objects.get(tracks=from_global_id(id)[1])
                    new_playlist = Playlist.objects.get(pk=from_global_id(playlist)[1])
                    old_playlist.tracks.remove(track_instance)
                    new_playlist.tracks.add(track_instance)
        
                # Update the updated_at time
                track_instance.updated_at = timezone.now()

                track_instance.save()
                return UpdateTrack(ok=ok, track=track_instance, user=user)
            return UpdateTrack(ok=ok, track=None, user=user)

class DeleteTrack(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the track to be deleted")

    ok = graphene.Boolean(description="Success status")
    user = graphene.String(description="Username of the authenticated user")

    @staticmethod
    def mutate(root, info, id):
        user = check_logged_in(info)
        if user:
            obj = Track.objects.get(pk=from_global_id(id)[1])
            obj.delete()
            return DeleteTrack(ok=True, user=user)

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True, description="A new username")
        password = graphene.String(required=True, description="A secure password")

    def mutate(self, info, username, password):
        user = get_user_model()(
            username=username,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    create_topic = CreateTopic.Field()
    update_topic = UpdateTopic.Field()
    delete_topic = DeleteTopic.Field()
    
    create_playlist = CreatePlaylist.Field()
    update_playlist = UpdatePlaylist.Field()
    delete_playlist = DeletePlaylist.Field()

    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    
    create_language = CreateLanguage.Field()
    update_language = UpdateLanguage.Field()
    delete_language = DeleteLanguage.Field()
    create_user = CreateUser.Field()
    
    # Authentication fields
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

class Query(graphene.ObjectType):
    #get_language = graphene.List(LanguageType, id=graphene.Int(description="ID of the language object"), active=graphene.Boolean(description="The active status of the object"), published=graphene.Boolean(description="The published status of the object"))
    #get_track = graphene.List(TrackType, id=graphene.Int(description="ID of the track object"), index=graphene.Int(description="Position of the track within a playlist"), active=graphene.Boolean(description="The active status of the object"), published=graphene.Boolean(description="The published status of the object"), language=graphene.ID(description="The language of the track"))
    #get_topic = graphene.List(TopicType, id=graphene.Int(description="ID of the topic object"), index=graphene.Int(description="Position of the topic in the interface"), active=graphene.Boolean(description="The active status of the object"), published=graphene.Boolean(description="The published status of the object"), language=graphene.ID(description="The language of the topic"))
    #get_playlist = graphene.List(PlaylistType, id=graphene.Int(description="ID of the playlist object"), index=graphene.Int(description="Position of the playlist within a topic"), active=graphene.Boolean(description="The active status of the object"), published=graphene.Boolean(description="The published status of the object"), language=graphene.ID(description="The language of the playlist"))

    language = relay.Node.Field(LanguageType)
    topic = relay.Node.Field(TopicType)
    playlist = relay.Node.Field(PlaylistType)
    track = relay.Node.Field(TrackType)

    all_languages = DjangoFilterConnectionField(LanguageType)
    all_topics = DjangoFilterConnectionField(TopicType)
    all_playlists = DjangoFilterConnectionField(PlaylistType)
    all_tracks = DjangoFilterConnectionField(TrackType)
    
    all_users = graphene.List(UserType)
    current_user = graphene.Field(UserType)
    
    def resolve_all_users(scelf, info):
        #if check_logged_in(info):
        return get_user_model().objects.all()

    def resolve_current_user(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user
    """
    # get topic by id
    def resolve_get_track(self, info, **kwargs):
        args = dict(kwargs)
        if 'id' in args:
            args['pk'] = args['id']
            del args['id']
        if 'language' in args:
            args['language_id'] = args['language']
            del args['language']
        return Track.objects.filter(**args)

    def resolve_get_topic(self, info, **kwargs):
        args = dict(kwargs)
        if 'id' in args:
            args['pk'] = args['id']
            del args['id']
        if 'language' in args:
            args['language_id'] = args['language']
            del args['language']
        return Topic.objects.filter(**args)

    def resolve_get_playlist(self, info, **kwargs):
        args = dict(kwargs)
        if 'id' in args:
            args['pk'] = args['id']
            del args['id']
        if 'language' in args:
            args['language_id'] = args['language']
            del args['language']
        return Playlist.objects.filter(**args)

    def resolve_get_language(self, info, **kwargs):
        args = dict(kwargs)
        if 'id' in args:
            args['pk'] = args['id']
            del args['id']
        return Language.objects.filter(**args)

    # get tracks by playlist
    def resolve_tracks(self, info, playlist = None, **kwargs):

        if playlist is not None:            
            return Track.objects.filter(playlist__id=playlist)
        return None

    # get playlist by topic
    def resolve_playlists(self, info, topic = None, **kwargs):

        if topic is not None:            
            return Playlist.objects.filter(topic__id=topic)
        
        return None
    
    # get all languages/topics/playlists/tracks in database
    def resolve_all_languages(self, info, **kwargs):
        #if check_logged_in(info):
        return Language.objects.all()

    def resolve_all_topics(self, info, **kwargs):
        #if check_logged_in(info):
        return Topic.objects.all()

    def resolve_all_playlists(self, info, **kwargs):
        #if check_logged_in(info):
        return Playlist.objects.all()

    def resolve_all_tracks(self, info, **kwargs):
        #if check_logged_in(info):
        return Track.objects.all()
    """

"""
def fill_data(csv):
    import pandas as pd
    data = pd.read_csv(csv)

    # Create language
    english = Language(
        name = "English",
        audio_url = "",
        published = True,
        )
    english.save()

    topics = data.topic.unique()

    for topic_n, topic in enumerate(topics):
        # create topic here
        topic_instance = Topic(
            index = topic_n,
            title=topic,
            audio_url = "",
            active = True,
            published = True,
            language_id = english.pk
            )
        topic_instance.save()

        playlists = data.loc[data['topic'] == topic].playlist.unique()
        for playlist_n, playlist in enumerate(playlists):
            # create playlist object here
            playlist_instance = Playlist(
                index = playlist_n,
                title=playlist,
                audio_url = "",
                active = True,
                published = True,
                language_id = english.pk
                )
            playlist_instance.save()

            tracks = data.loc[data['playlist'] == playlist].track.unique()
            for track_n, track in enumerate(tracks):
                #create track object here
                track_row = data.loc[data['track'] == track]
 
                track_instance = Track(
                    index = track_n,
                    title=track,
                    audio_url = track_row.audio.item(),
                    transcript = track_row.transcript.item(),
                    duration = "0",
                    created_at = timezone.now(),
                    updated_at = timezone.now(),
                    active = True,
                    published = True,
                    language_id = english.pk
                    )
                track_instance.save()
                playlist_instance.tracks.add(track_instance)

            topic_instance.playlists.add(playlist_instance)
                
"""
# Create user
"""
user = get_user_model()(
    username="test",
)
user.set_password("test")
user.save()
"""
#fill_data("data.csv")

schema = graphene.Schema(query=Query, mutation=Mutation)