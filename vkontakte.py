import time

import requests

from utils import batch


class VKApi:
    BASE_URL = "https://api.vk.com/method"
    API_VERSION = "5.9"

    def __init__(self, vk_token):
        self.vk_token = vk_token

    def get_streaming_url(self):
        method = 'streaming.getServerUrl'

        response = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={self.vk_token}").json()[
            'response']

        endpoint = response.get('endpoint')
        key = response.get('key')
        return endpoint, key

    def get_group_members(self, group_id, total_count, offset=0, fields=None):
        """
        try overcoming VK limitations with the help of offsets. 1000 only for 1 request

        :param group_id:
        :param total_count:
        :param offset:
        :param fields:
        :return:
        """
        method = 'groups.getMembers'
        params = {
            "group_id": group_id,
            "sort": "id_asc",
        }

        if fields is not None:
            params['fields'] = ','.join(fields)

        # max batch size = 1000 on VK side
        needed_iterations = total_count // 1000
        flat_amount = total_count % 1000
        ids = []

        for i in range(needed_iterations):
            params['offset'] = offset + (i * 1000)
            pack = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={self.vk_token}",
                                params=params).json()['response']['items']
            ids.extend(pack)

        if flat_amount:
            if not params.get('offset'):
                params['offset'] = 0
            else:
                params['offset'] += 1000

            params['count'] = flat_amount
            last_batch = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={self.vk_token}",
                                      params=params).json()

            ids.extend(last_batch)

        return ids

    def search(self, filter_params, user_token):
        method = 'users.search'

        allowed_query_params = ['city', 'country', 'age_from', 'age_to', 'fields', 'count', 'sex',
                                'birth_day', 'birth_month', 'birth_year', 'group_id', 'sort']
        for i in filter_params.keys():
            if i not in allowed_query_params:
                print(i)
        assert all(i in allowed_query_params for i in filter_params.keys())

        users = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={user_token}",
                             params=filter_params).json()

        return users['response']['items']

    def get_users_messages(self, ids, token):
        """
        the idea is to make 1 execute query instead of 25 wall.get. On practice it doesn't work, and every wall.get
        inside "execute" is counted by VK. Anyway, I was lazy to rewrite, it works either way
        :param ids: list of ids whose message we want to get
        :param token: access_token
        :return: list of objects describing users with their messages
        """
        method = "execute"
        response = []
        full = len(ids) // 25
        count = 1
        for pack in batch(list(ids), 25):
            print(f"***Batch {count} out of {full}...")
            length = len(pack)
            vk_code = f"""
            var response = [];
            var ids = {pack};
            var count = 0;
            while (count != {length - 1}) {{
                response.push( {{"id": ids[count], "messages": API.wall.get( {{"owner_id": ids[count], "count": 10, "filter": "owner"}} ) }});
                count = count + 1;
            }}
            return response;
            """
            try:
                response.extend(requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={token}",
                                             params={"code": vk_code}).json()['response'])
            except KeyError:
                print(requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={token}",
                                   params={"code": vk_code}).json())
            count += 1
            time.sleep(1)
        return response

    def get_wall_posts(self, grp_or_user_id, count, token):
        """
        get posts from group walls 1 by 1. It's easier than collecting 10000000000 users

        :param grp_or_user_id: vk_id of a group or a user. we can still use this function to get walls of people
        :param count: how many?
        :param token: access_token
        :return: list of posts with info on users / groups
        """
        method = 'wall.get'

        assert count <= 100

        params = {'owner_id': grp_or_user_id, 'count': count, 'filter': 'owner'}
        posts = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={token}",
                             params=params).json()
        return posts

    def get_comments(self, grp_or_user_id, post_id, count, token):
        """
        get comments to posts from groups or walls

        :param grp_or_user_id: vk_id of a group or a user
        :param post_id: id of a message / post
        :param count: how many comments?
        :param token: vk access_token
        :return: comments with info
        """
        method = 'wall.getComments'

        params = {'owner_id': grp_or_user_id, 'post_id': post_id, 'need_likes': 1, 'count': count, 'extended': 1}

        comments = requests.get(f"{self.BASE_URL}/{method}?v=5.92&access_token={token}",
                                params=params).json()
        return comments
