'''Script to be called periodically to check that videos
are still available. Cycles through videos currently in DB
sorted by the last time they were accessed. If video still exists
record is added of time of last checking; else first time of being
found missing is recorded.

If script is interrupted, can be restarted from a particular video
with argument -r <videoId>
'''
import sys,time,operator,re,requests
from pymongo import MongoClient
import collections
client = MongoClient()
db=client.yt_db
# Set up mongodb client
import time
n=0

restartId=-999

if '-r' in sys.argv:
    index=sys.argv.index('-r')
    restartId=sys.argv[index+1]
    print 'RESTART AT',restartId
    time.sleep(3)
  
for v in db.VIDEOS.find({}).sort('retrieved.-1',1):
    if n%500==0:print n,'...'

    skip=False

    if u'videoId' in v.keys():

      if v[u'videoId']==restartId:
        restartId=-999
        print '...RESTARTING'
    else:
        print '\tKEY ERROR'
        print '\t',v.keys()
#    sys.exit(1)
        skip=False
    
    if restartId==-999 or not skip:

        requestUrl='https://gdata.youtube.com/feeds/api/videos/'+v[u'videoId']+'?v=2&alt=json'
        d=requests.get(requestUrl)
      
        while re.search(r'too_many_recent_calls|ServiceUnavailableException',d.text):
            print 'API THRASHED OR UNAVAILABLE, SLEEPING...'
            time.sleep(60)
            requestUrl='https://gdata.youtube.com/feeds/api/videos/'+v[u'videoId']+'?v=2&alt=json'
            d=requests.get(requestUrl)
   
        if re.search(r'Private video|ResourceNotFoundException|User authentication required',d.text) or d.status_code==404:
            print v.keys()
#      db.VIDEOS.update({u'id':v[u'videoId']},{'$addToSet':{u'missing':time.time()}})
            if not 'missing' in v.keys():
                db.VIDEOS.update({u'videoId':v[u'videoId']},{'$set':{u'missing':time.time()}},upsert=False)
                db.VIDEOS.update({u'videoId':v[u'videoId']},{'$set':{u'missingReason':[d.text,d.status_code]}},upsert=False)

            print 'MISSING',v['videoId']
            print d.text
            time.sleep(5)
            # This could mean private or account closed
        elif not d.status_code==200:
            print v[u'id']['videoId']
            print d.status_code,d.text
            sys.exit(1)
        else:
            print 'STILL THERE...',v[u'retrieved'][-1]
            if not type(v[u'retrieved'])==list:
                print 'NOT LIST'
                sys.exit(1)
        try:
            nViews=int(d.json()['entry']['yt$statistics']['viewCount'])
#        nFavs=int(d.json()['entry']['yt$statistics']['favouriteCount'])
            print nViews,v['videoId']
            db.VIDEOS.update({u"videoId":v[u"videoId"]},{"$addToSet":{u"views":nViews}})
#        db.VIDEOS.update({u"videoId":v[u"videoId"]},{"$addToSet":{u"favourites":nFavs}})
        
        except:
	        print 'NO VIEW COUNT TO UPDATE'
            db.VIDEOS.update({u"videoId":v[u"videoId"]},{"$addToSet":{u"retrieved":time.time()}})
            print 'UPDATING',v['videoId']
    n+=1
