import string

import peewee
from nltk import word_tokenize, sent_tokenize

from playhouse.postgres_ext import ArrayField

pg_db = peewee.PostgresqlDatabase('diplom', user='postgres', password='1',
                                  host='localhost', port=5432, autocommit=True, autorollback=True)


class GroupPost(peewee.Model):
    text = peewee.TextField()
    group_id = peewee.IntegerField()
    vk_id = peewee.IntegerField(unique=True)

    class Meta:
        database = pg_db


class PostComment(peewee.Model):
    likes = peewee.IntegerField()
    text = peewee.TextField()
    post = peewee.ForeignKeyField(GroupPost, backref='comments', on_delete='CASCADE')
    comments_to_comment = peewee.IntegerField(null=True)  # amount of comments to a comment
    vk_id = peewee.IntegerField(unique=True)

    class Meta:
        database = pg_db


class User(peewee.Model):
    nick = peewee.TextField(unique=True)
    name = peewee.TextField(null=True)
    friends = ArrayField(peewee.TextField, null=True)
    friend_of = ArrayField(peewee.TextField, null=True)
    birthdate = peewee.TextField(null=True)
    city = peewee.TextField(null=True)
    country = peewee.TextField(null=True)
    schools = ArrayField(peewee.TextField, null=True)
    interests = ArrayField(peewee.TextField, null=True)
    about = peewee.TextField(null=True)
    title = peewee.TextField(null=True)
    subtitle = peewee.TextField(null=True)
    picture = peewee.TextField(null=True)
    source = peewee.CharField(max_length=100)
    sex = peewee.CharField(max_length=10, null=True)
    additional = peewee.TextField(null=True)
    vk_id = peewee.IntegerField(null=True)
    creation_ts = peewee.DateTimeField(null=True)

    class Meta:
        database = pg_db


class Message(peewee.Model):
    author = peewee.ForeignKeyField(User, backref='messages', on_delete='CASCADE')
    message = peewee.TextField()
    link = peewee.TextField(unique=True)
    date = peewee.TextField()

    class Meta:
        database = pg_db

    @property
    def symbols_count(self):
        return len(self.message)

    @staticmethod
    def tokenize_words(message):
        return [i for i in word_tokenize(message) if i not in string.punctuation]

    @property
    def words_count(self):
        return len(self.message.tokenize_words())

    @property
    def sentences_count(self):
        return len(sent_tokenize(self.message, 'russian'))

    @property
    def comas(self):
        return self.message.count(",")

    @property
    def tires(self):
        return self.message.count("-") + self.message.count("—")

    @property
    def first_sentence(self):
        return sent_tokenize(self.message, 'russian')[0]

    @property
    def last_sentence(self):
        return sent_tokenize(self.message, 'russian')[-1]


pg_db.create_tables([User, Message, GroupPost, PostComment])
