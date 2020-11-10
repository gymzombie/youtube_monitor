# coding: utf-8
'''Convenience script to add random number to each video.
Used in web interface to display a random video.'''

import random,sys
from pymongo import MongoClient
client = MongoClient()
db=client.yt_db

if True:
    q=db.VIDEOS.find()
    n=0
    for v in q:
    #  print v,v.keys()
    #  print v['_id']
        db.VIDEOS.update({'_id':v['_id']},{'$set':{'randId':random.random()}})
        if n%1000==0:
            print(n)
        n+=1
else:
    # Quick test of random selection
    for i in range(10):
        coinToss1=random.random()
        coinToss2=random.random()
        print(coinToss1,coinToss2)
        if coinToss1>coinToss2:
            q=db.VIDEOS.find({'randId':{'$gt':coinToss2,'$lt':coinToss1}}).sort([('randId',1)]).limit(1)
        else:
            q=db.VIDEOS.find({'randId':{'$gt':coinToss1,'$lt':coinToss2}}).sort([('randId',1)]).limit(1)
        for v in q:
            print(v['videoId'])
