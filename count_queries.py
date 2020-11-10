# coding: utf-8
'''Convenience function to count all videos matching
a given query; called with each daily update. These 
totals are stored in collection: 
QUERIES to be displayed in web interface'''

from pymongo import MongoClient

client = MongoClient()
db = client.yt_db

q = db.VIDEOS.aggregate(
    [{'$match': {'query': {'$exists': 'True'}}}, {'$group': {'_id': {'query': '$query'}, 'number': {'$sum': 1}}}])

for qq in q['result']:
    db.QUERIES.update({'query': qq['_id']['query'][0]}, {'query': qq['_id']['query'][0], 'count': qq['number']}, True)
