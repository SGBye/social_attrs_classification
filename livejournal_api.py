import os

import requests


class LiveJournalApi:
    """
    3 methods for gathering user's info from LiveJournal
    """
    def gather_personal_info(self, nick):
        """
        first download the personal data from the internet.
        May be slower, but for now more polite.
        """

        data = requests.get(f'https://{nick}.livejournal.com/data/foaf',
                            params={'email': 'ctac1995@gmail.com'})

        # create folder to cache and write data
        with open(os.path.join('cache', f'{nick}', f'{nick}_profile.xml'), 'w',
                  encoding='utf-8') as f:
            f.write(data.text)
        return data.text

    def gather_connections(self, nick):
        """
        first download the profile-communities connections data from the internet.
        May be slower, but for now more polite.
        """
        data = requests.get(f'https://www.livejournal.com/misc/fdata.bml?conn=1&user={nick}',
                            params={'email': 'ctac1995@gmail.com'})
        with open(os.path.join('cache', f'{nick}', f'{nick}_connections.txt'), 'w', encoding='utf-8') as f:
            f.write(data.text)
        return data.text

    def gather_messages(self, nick):
        """
        first download the messages data from the internet.
        May be slower, but for now more polite.
        """
        data = requests.get(f'https://{nick}.livejournal.com/data/atom',
                            params={'email': 'ctac1995@gmail.com'})
        with open(os.path.join('cache', f'{nick}', f'{nick}_messages.html'), 'w', encoding='utf-8') as f:
            f.write(data.text)
        return data.text
