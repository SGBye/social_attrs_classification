import json
import re
from datetime import date

import requests

from models import User, Message
from settings import VK_TOKEN
from vkontakte import VKApi

ID_REGEX = re.compile(r"^id\d+$")

vk_api = VKApi(VK_TOKEN)
VK_USER_TOKEN = NotImplemented  # Just put here access token you got from VK

ria_news_id = 15755094
vk_music_id = 147845620
vk_team = 22822305

vk_link_pattern = "https://vk.com/id{user_id}?w=wall{user_id}_{message_id}%2Fall"


def write_messages(users: User, filename: str):
    with open(filename, 'w', encoding='utf8') as f:
        for user in users:
            for message in user.messages:
                f.write(' '.join(message.message.split('\n')) + '\n')


def create_users_by_gender_and_group(sex, group_id):
    sex_id = 1 if sex == 'female' else 2

    users = vk_api.search({
        'sex': sex_id,
        'sort': 2,  # you can change sort to get more users, coz usually vk gives only 1000. So 1000 asc, then 1000 desc
        'group_id': group_id,
        'fields': 'bdate,sex,interests,domain,city,country',
        'count': 1000
    }, VK_USER_TOKEN)
    count = 0
    for user in users:
        # check if exists. With Django it would be much-much easier :cccc
        try:
            User.create(nick=user.get('domain', user['id']),
                        birthdate=user.get('bdate'),
                        interests=user.get('interests', '').split(','),
                        source='vkontakte', sex=sex,
                        city=user.get('city', {}).get('title'),
                        country=user.get('country', {}).get('title'),
                        vk_id=user.get('id'))
        except:
            # yes, it's really dirty, but it works. I focused more on models training
            try:
                count += 1
                query = User.update(birthdate=user.get('bdate'),
                                    interests=user.get('interests', '').split(','),
                                    source='vkontakte', sex=sex,
                                    city=user.get('city', {}).get('title'),
                                    country=user.get('country', {}).get('title'),
                                    vk_id=user.get('id')).where(User.nick == user.get('domain', user['id']))
                query.execute()
                print(count)
            except Exception as exc:
                print(exc)
                continue
    return users


def create_messages(ids, filename):
    c = vk_api.get_users_messages(ids, VK_USER_TOKEN)

    with open('create_messages.json', 'w', encoding='utf8') as f:
        json.dump(c, f)

    with open(filename, 'w', encoding='utf8') as f:
        for i in c:
            author_id = User.get(User.vk_id == i['id'])
            if isinstance(i['messages'], dict):
                for b in i['messages']['items']:
                    try:
                        Message.create(link=vk_link_pattern.format(user_id=i['id'], message_id=b['id']),
                                       message=' '.join(b['text'].split('\n')),
                                       author=author_id,
                                       date=date.fromtimestamp(b['date']))
                        f.write(' '.join(b['text'].split('\n')) + '\n')

                    except Exception as exc:
                        print(exc)
                        continue


if __name__ == "__main__":
    # first create users in the database, passing gender and group_id
    users = create_users_by_gender_and_group('male', vk_team)

    # then get ids of created users
    ids = [user['id'] for user in users]

    # finally create messages
    create_messages(ids, 'test_vk_team.txt')

    # and write those message if you need them at once
    write_messages(users, "male_vk_team.txt")

