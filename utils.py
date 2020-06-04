import re


class LiveJournalMessage:
    """
    utility class for working with LiveJournal messages. In fact, it's not that important
    """
    def __init__(self, message, link, date):
        self.message = message
        self.link = link
        self.date = date

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.message[:50]}..."


def clean_tags(raw_html):
    """
    clean messages from html tags and quotes
    """

    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    quotes = re.compile('&quot;')
    change_quoes = re.sub(quotes, '"', cleantext)
    to_delete = re.compile("&\w+;")
    cleantext = re.sub(to_delete, '', change_quoes)
    return cleantext


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
