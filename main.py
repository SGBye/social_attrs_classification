from models import User

from users import LiveJournalUser


# this function is just an example. In fact, first you create a user and then get more and more iterating over their
# friends
def collect_users_friends(nickname: str, index_start: int, index_end: int):
    """
    collect info about a user's friends to fill the database

    :param nickname: one of already processsed LiveJournal users
    :param index_start: start offset of friends
    :param index_end: end offset of friends
    :return: None
    """
    user = User.get(nick=nickname)

    global_count = 0
    for index, friend in enumerate(user.friends[index_start:index_end]):
        local_count = 0
        global_count += 1
        try:
            a = User.get(nick=friend)
        except:
            a = LiveJournalUser(nick=friend)
            a.fill_the_data()
        for new_person in a.friends:
            local_count += 1
            if not new_person.startswith('_'):
                print(f"Processing {local_count} of {global_count} out of {len(a.friends)}...")
                # primitive get_or_create from Django
                try:
                    User.get(nick=new_person)
                    continue
                except:
                    new_user = LiveJournalUser(new_person)
                    new_user.fill_the_data()


if __name__ == "__main__":
    collect_users_friends("smitrich", 10, 60)

