import logging
import os
import time
import xml.etree.ElementTree as ET
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from iso3166 import countries

from exceptions import NotFetchedException
from livejournal_api import LiveJournalApi
from models import User, Message
from settings import MAX_RETRIES, SENTENCES_TO_COLLECT
from utils import clean_tags, LiveJournalMessage

log = logging.getLogger(__name__)


class BaseUser:

    def __init__(self):
        self.birthdate = None  # done
        self.city = None  # done
        self.country = None  # done
        self.interests = []  # done
        self.about = None  # done


class LiveJournalUser(BaseUser):
    api = LiveJournalApi()
    """
    describes the fields and functions for processing the data gathered from LiveJournal for a specific nickname
    """

    def __init__(self, nick):
        super().__init__()
        self.nick = nick
        self.name = None
        self.friends = []  # done
        self.friend_of = []  # done
        self.schools = []  # done
        self.about = None  # done
        self.title = None
        self.subtitle = None
        self.picture = None
        self.source = 'livejournal'

    def __str__(self):
        return f'Ник: {self.nick}, имя: {self.name}, дата рождения: {self.birthdate}'

    def __repr__(self):
        return self.__str__

    def fill_the_data(self):
        filename = os.path.join('cache', f'{self.nick}')
        os.makedirs(filename, exist_ok=True)
        try:
            self.process_personal_info()
            self.process_connections()
        except NotFetchedException:
            return

        db_user = self.db_create()
        try:
            messages = self.process_messages()
        except NotFetchedException:
            return

        prepared_data = [
            (db_user, message.message, message.date, message.link) for message in messages
        ]
        Message.insert_many(prepared_data, fields=[Message.author, Message.message, Message.date, Message.link]).execute()

    def process_personal_info(self):
        """
        process the xml downloaded from the internet or from local cache
        """
        try:
            tree = ET.parse(os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml'))
        except FileNotFoundError:
            # retries logic
            for attempt in range(MAX_RETRIES):
                try:
                    tree = ET.ElementTree(ET.fromstring(self.api.gather_personal_info(self.nick)))
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
                else:
                    break
            # if we failed all attempts, just forget about this guy
            else:
                raise NotFetchedException

        except ET.ParseError:
            log.debug('This user has either been deleted or never created: %s', self.nick)
            return

        root = tree.getroot()[0]

        for i in root:
            # get all the possible data from source
            if 'name' in i.tag:
                self.name = i.text
            elif 'journaltitle' in i.tag:
                self.title = i.text
            elif 'img' in i.tag:
                for key in i.attrib:
                    if 'resource' in key:
                        self.picture = i.attrib[key]
            elif 'journalsubtitle' in i.tag:
                self.subtitle = i.text
            elif 'dateOfBirth' in i.tag:
                self.birthdate = i.text
            elif 'city' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        self.city = unquote(i.attrib[key])
            elif 'country' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        try:
                            self.country = countries.get(i.attrib[key]).name
                        except KeyError:
                            self.country = i.attrib[key]
            elif 'school' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        self.schools.append(i.attrib[key])
            elif 'interest' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        self.interests.append(i.attrib[key])
            elif 'bio' in i.tag:
                try:
                    self.about = clean_tags(i.text)
                except TypeError:
                    print(self)

    def process_connections(self):
        """
        process the html downloaded from the internet or from local cache
        """

        try:  # if it's not the first call to user's data, we should use cache
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_connections.txt'),
                      encoding='utf-8') as f:
                data = f.readlines()
        except FileNotFoundError:
            # retries logic
            for attempt in range(MAX_RETRIES):
                try:
                    data = self.api.gather_connections(self.nick).split('\n')
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
                else:
                    break
            # failing all attempts makes us forget the guy
            else:
                raise NotFetchedException

        for line in data:
            if len(line) > 2:  # it's in the following format "C< username"
                if not line.startswith('#'):
                    if '>' in line:
                        self.friends.append(line.split()[1])
                    else:
                        self.friend_of.append(line.split()[1])

    def process_messages(self):
        """
        process the html downloaded from the internet or from local cache
        """

        try:
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_messages.html'), encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            # retries logic
            for attempt in range(MAX_RETRIES):
                try:
                    html = self.api.gather_messages(self.nick)
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
                else:
                    break
            # failing all attempts makes us forget the guy
            else:
                raise NotFetchedException

        soup = BeautifulSoup(html, 'html.parser')
        messages = []
        for tag in soup.find_all('entry'):
            if len(messages) < SENTENCES_TO_COLLECT:
                message = ''
                if tag.content:
                    message = clean_tags(tag.content.text)
                elif tag.summary:
                    message = clean_tags(tag.summary.text)
                messages.append(LiveJournalMessage(message=message,
                                                   link=tag.link['href'],
                                                   date=tag.published.text.split('T')[0]))
        return messages

    def db_create(self):
        a_user, created = User.get_or_create(nick=self.nick)
        if created:
            q = User.update(self.__dict__).where(User.nick == self.nick)
            q.execute()
        return User.get(nick=self.nick)
