'''Script to compile all text associated with a video together.
Includes video title, summary and all comments. Once this text is cleaned
and normalised, NLP can be applied. Text for each video commited to database'''

import sys,re
from datetime import date,datetime
import datetime,time
import requests
import utils
from settings import *
import langid
from regex import *
from pymongo import MongoClient
from normalise_file import getWordLists
client = MongoClient()
db=client.yt_db
# Set up mongodb client

n=0

targetLangs=['ar','fa']

numberDateRe='([0-9/]+)'

allRe='|'.join([harakatRe,hahRe,tuhaRe,alRe,hahRe,wawRe,alifMaksourRe,alifRe,hashRe,underscoreRe,puncRe,numberDateRe])

stopWords,negationWords,exemptWords,posEmojis,negEmojis=getWordLists()
# Get list of reference words

####################
def clean(content):
####################
# Add language testing here and removal of punctuation etc
# taken from normalisatino code
    global stopwords
    reject=True

    for l in langid.rank(content):
        if l[0] in targetLangs and l[1]>0.7:
            reject=False
    # If content is detected as Arabic/Farsi with reasonable
    # confidence then consider it
    if reject:
        return None
    else:
        content=content.split(' ')
        content=[re.sub(allRe,'',c) for c in content if not c in stopWords]
        content=[re.sub(hahaRe,u'ههه') for c in stopWords]
        content=' '.join(content)
        return content
###########
def main():
###########
#    print allRe
#    sys.exit(1)

    n=0

    for v in db.VIDEOS.find({'missing':{'$exists':False}}):
        n+=1

        if (n+1)%100==0:print 'VIDEO',n
#        print v['videoId']

        nComment=db.COMMENTS.find({'videoId':v['videoId']}).count()

        videoString=''

        try:
            videoString=videoString+' '+clean(v['title'])
        except:
#            print '!!! NO TITLE'
            continue

        try:
#            print '===>',v['description']
            videoString=videoString+' '+clean(v['description'])
        except:
#            print '!!! NO DESCRIPTION'
            continue
        nComments=0            
        for c in db.COMMENTS.find({'videoId':v['videoId']}):

            try:
                videoString=videoString+' '+clean(c['content'])
                nComments+=1
            except:
#            print '!!! NO CONTENT'
                continue
                # Quite common
#        print videoString,nComments,'COMMENTS'
#        print ''
#        if n==100:break
        db.TOPIC_STRINGS.insert({'videoId':v['videoId'],'doc':videoString,'nComments':nComments})
if __name__=='__main__':
    main()
