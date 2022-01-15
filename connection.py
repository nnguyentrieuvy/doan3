import pymongo
from django.conf import settings

def connect_db():
    my_client = pymongo.MongoClient(host=['localhost:27017'])
    DVX = my_client['DatVeXe']
    return DVX