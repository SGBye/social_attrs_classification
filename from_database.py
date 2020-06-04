import datetime
import os
from models import Message, User

# users = User.select().where(User.source != 'vkontakte')
from users import LiveJournalUser

# do whatever queries you'd like, examples below
female_messages = Message.select().join(User).where(User.sex == 'female')

# write the messages to file
with open('female_messages.txt', 'w', encoding='utf8') as f:
    for message in female_messages:
        if len(message.message) > 50:
            f.write(message.message + '\n')
