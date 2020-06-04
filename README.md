# social_attrs_classification
This repo contains files demonstrating work with LiveJournal and VK APIs. 

exceptions.py >>>>> just a simple exception for LiveJournal API mainly
from_database.py >>>>> demonstrates simplicity of queries using peewee
livejournal_api.py >>>>>> a class for making calls to LiveJournal API. Just make an instance to get access to it's methods
main.py >>>>> demonstrates the process of collecting data about LiveJournal users. First you get info about a user, then iterate over his friends / the friends of his friends etc.
models.py >>>>> contains models describing database tables (peewee /* I wish it were Django, really */)
settings.py >>>>> settings for a project, like tokens, amount of messages etc.
users.py >>>>> utility classes for working with users. Actually they could be extended for anything, but on practice it was easier to work with raw data :/
utils.py >>>>> utility function to help processing data etc.
vkontakte.py >>>>> class for working with VK API
