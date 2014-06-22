# coding: utf-8
'''Script to search for videos matching a given
keyword posted to YouTube in the last 24 hours.
Queries public API (key taken from settings.py)
grabs video information, comments and user details
and stores in database.

Makes series of API calls to find new videos from
last 24 hours, in hourly increments. Makes new calls
to get full information for each video, and makes further
calls to get all comments and comment authors.
'''
import sys,re
from datetime import date,datetime
import datetime,time
import requests
import utils
from settings import *

from pymongo import MongoClient
client = MongoClient()
db=client.yt_db
# Set up mongodb client

from dateutil.rrule import rrule, DAILY, HOURLY

nVideos=0
nComments=0

QUERY=u'شلل الاطفال'
#QUERY=u'سوريا'

diff=0

if '-n' in sys.argv:
    index=(sys.argv).index('-n')
    diff=int(sys.argv[index+1])
    print 'SET DAY DIFFERENCE'

if '-q' in sys.argv:
    QUERY=''
    index=(sys.argv).index('-q')
    QUERY=u'+'.join([q.decode('utf-8') for q in sys.argv[index+1:]])
#  print 'QUERY IS>>'+QUERY+'<<'
############
def addAuthorToMongo(authorId):
############
    '''Receives YouTube user ID (str) and
    gets information from API and adds to DB'''
    global QUERY

    print 'ADDING AUTHOR TO MONGO...',authorId

    dRaw=None
    nError=0
    skip=False

    if authorId=='__NO_YOUTUBE_ACCOUNT__':
        dRaw='ERROR'
    return None

    while not dRaw:
        try:
            print 'GETTING DATA'
            dRaw=requests.get('http://gdata.youtube.com/feeds/api/users/'+authorId+'?v=2&alt=json')
        except:
            print '\t\tAUTHOR INFO REQUEST FAILED'
            print '\t\t',id
            time.sleep(60)
            nError+=1
            print 'nError',nError
            
            if nError==10:  
                skip=True
                dRaw='ERROR'
                print 'Breaking'
                break
        if not skip:
            while not dRaw.status_code in [200,201]:
                print 'TOO MANY REQUESTS OR API UNAVAILABLE! SLEEPING....',
                logFile.writerow([getTime(startTime),'API UNAVAILABLE',dRaw.status_code,dRaw.text.encode('utf-8')])
                print dRaw.status_code
                print dRaw.text
                print getTime(startTime)
                time.sleep(60)
                dRaw=requests.get('http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json')

    d=dRaw.json()
    print 'GOT AUTHOR DATA...'
#    print d
    returnData={'retrieved':[int(time.time())],'query':[QUERY]}

    try:
        returnData['id']=d['entry']['author'][0]['yt$userId']['$t']
    except:
        print 'AUTHOR MISSING ID: SKIPPING'
        return None

    try:
        returnData['name']=d['entry']['author'][0]['name']['$t']
    except:
        print 'AUTHOR MISSING NAME'

    try:
        returnData['link']=d['entry']['link'][0]['href']
    except:
        print 'AUTHOR MISSING LINK'
    
    try:
        returnData['subscriberCount']=int(d['entry']['yt$statistics']['subscriberCount'])
    except:
        print 'AUTHOR SUB COUNT'

    try:
        returnData['viewCount']=int(d['entry']['yt$statistics']['viewCount'])
    except:
        print 'AUTHOR VIEW COUNT'

    try:
        returnData['watchCount']=int(d['entry']['yt$statistics']['videoWatchCount'])
    except:
        print 'AUTHOR WATCH COUNT'

    try:
        returnData['totalViews']=int(d['entry']['yt$statistics']['totalUploadViews'])
    except:
        print 'AUTHOR UPLOAD VIEWS COUNT'

    try:
        returnData['location']=d['entry']['yt$location']['$t']
    except:
        print 'AUTHOR LOCATION'

    try:
        returnData['summary']=d['entry']['summary']['$t']
    except:
        print 'AUTHOR SUMMARY'
#    print returnData.keys()
#    print returnData
#    sys.exit(1)

   ###########################################
    nMatches=db.AUTHORS.find({'id':returnData['id']}).count()

    print '!!!!!!!!NMATCHES',nMatches

    if nMatches==0:
        db.AUTHORS.insert(returnData)
        print '\tAUTHOR IS NEW. ADDING...'
    elif nMatches==1:
        db.AUTHORS.update(returnData,{"$addToSet":{u"retrieved":int(time.time())}})
        print '\tAUTHOR EXISTS. UPDATING'
    else:
        print '!!!!!WARNING: DUPLICATE AUTHOR',returnData,nMatches

    return returnData

############
def addCommentToMongo(comment):
############
    '''Takes comment as JSON object and adds to DB'''
    global QUERY
    returnData={'retrieved':[int(time.time())],'query':[QUERY]}

    try:
        returnData['commentId']=comment['id']['$t']
    except:
        print '\tMISSING ID SKIPPING'
        return None

    try:
        returnData['created']=comment['updated']['$t']
    except:
        print '\tMISSING CREATION TIME'
  
    try:
        returnData['authorName']=comment['author'][0]['name']['$t']
    except:
        print '\tMISSING AUTHOR NAME'

    try:
        returnData['authorId']=comment['author'][0]['yt$userId']['$t']
        addAuthorToMongo(returnData['authorId'])
    except:
        print '\tMISSING AUTHOR ID'

    try:
        returnData['content']=comment['content']['$t']
    except:
        print '\tMISSING CONTENT'

    try:
        returnData['videoId']=comment['yt$videoid']['$t'] 

    except:
        print '\tMISSING VIDEO ID'
#    return None
  ###########################################
    nMatches=db.COMMENTS.find({'commentId':returnData['commentId']}).count()
    print '!!!!COMMENTS MATCHES',nMatches

    if nMatches==0:
        db.COMMENTS.insert(returnData)
        print '\tCOMMENT IS NEW. ADDING...'
    elif nMatches==1:
        db.COMMENTS.update({'commentId':returnData['commentId']},{"$addToSet":{u"retrieved":int(time.time())}})
        print '\tCOMMENT EXISTS. UPDATING'
    else:
        print '!!!!!WARNING: DUPLICATE COMMENT',returnData,nMatches

#  print returnData

    return None

############
def putCommentsInMongo(v):
############
    '''Takes video ID (str), queries comment API
    and writes each comment on the video to DB'''
    global nComments
  
    commentsLink='https://gdata.youtube.com/feeds/api/videos/'+v+'/comments?v=2'+'&alt=json&max-results=50'
  # Get first page of results with 50 comments
  # Then check if a link to next page is ppresent

    comments=None
    nFail=0
    errorSkip=False

    while comments==None:

        commentsRaw=requests.get(commentsLink)
    
        while not commentsRaw.status_code==200:
            print commentsLink
            if re.search(r'Commenting is disabled for this video|User authentication required.|Resource not found',commentsRaw.text):
                print 'COMMENTS DISABLED FOR VIDEO/USER SIGNIN NEEDED/USER REMOVED VIDEO',v
            	print commentsRaw.text
                comments='ERROR'
                errorSkip=True
                break
            elif re.search(r'is too large to process',commentsRaw.text):
                print 'URL TOO LARGE TO PROCESS FOR VIDEO',v
            	comments='ERROR'
                commentsRaw=requests.get(commentsLink)
            	errorSkip=True
            	break
            elif re.search(r'too_many_recent_calls|Internal Server Error',commentsRaw.text):
            	print 'API ERROR SLEEPING...\n',commentsRaw.text
                time.sleep(60)
            	nFail+=1
            	if nFail==10:
            	    errorSkip=True
                    break
            else:
                print 'UNKNOWN ERROR'
                print commentsRaw.text
                print commentsRaw.status_code
                sys.exit(1)
        if not errorSkip:
            print 'ASSUMED GOT JSON OK...'
      ##################################
            comments=commentsRaw.json()
            nComments=comments['feed']['openSearch$totalResults']['$t']
            print v,'TOTAL NCOMMENTS',nComments
      ##################################
    
            if nComments>0 and 'entry' in comments['feed'].keys():
                print '\tNCOMMENTS',len(comments['feed']['entry'])
                for c,comm in enumerate(comments['feed']['entry']):
                    print '\nCOMMENT',c
                    nComments+=1
                    addCommentToMongo(comm)
    
            for l in comments[u'feed'][u'link']:
                if l['rel']=='next':
                    print '\tGOT NEXT PAGE'
                    commentsLink=l['href']
                    comments=None
            else:
                print 'SKIPPING'
                comments='ERROR'
                break
############
def putInMongo(videoData):
############
    '''Takes video data as JSON object and adds to DB.
    Checks for duplicates; if duplicated, records that 
    video was retrieved, else adds new record to DB'''
    nMatches=db.VIDEOS.find({u"videoId":videoData['videoId']}).count()
    ## find() returns cursor, doesn't read documents: faster

    if nMatches==0:
        db.VIDEOS.insert(videoData)
        print '\tVIDEO IS NEW. ADDING...'
    elif nMatches==1:
        try:db.VIDEOS.update({u"videoId":videoData[u'videoId']},{"$addToSet":{u"retrieved":int(time.time())}})
        except:print 'NO RETRIEVED TO UPDATE'
        try:db.VIDEOS.update({u"videoId":videoData[u'videoId']},{"$addToSet":{u"views":videoData['views'][0]}})
        except:print 'NO VIEWS TO UPDATE'
        try:db.VIDEOS.update({u"videoId":videoData[u'videoId']},{"$addToSet":{u"favourites":videoData['favourites'][0]}})
        except:print 'NO FAVOURITES TO UPDATE'
        # Record time retrieved, new view count, new favourite count
        print '\tVIDEO EXISTS. UPDATING'
    else:
        print '!!!!!WARNING: DUPLICATE VIDEOS',videoData[u'videoId'],nMatches
############
def getUsefulParts(videoData,vid):
############
    '''Cleans and simplifies JSON object representing
    video data returned from API.'''
    global QUERY
    returnData={'videoId':vid,'retrieved':[int(time.time())],'query':[QUERY]}
  ## i.e. watch at https://www.youtube.com/watch?v=<vid>
    try:
        returnData['category']=videoData[u'entry'][u'category'][1][u'label']
    except:
        print '\tNo category'

    try:
        returnData['views']=[int(videoData[u'entry'][u'yt$statistics'][u'viewCount'])]
    except:
        print '\tNo viewCount'

    try:
        returnData['favourites']=[int(videoData[u'entry'][u'yt$statistics'][u'favoriteCount'])]
    except:
        print '\tNo favouriteCount'

    try:
        returnData['authorName']=videoData[u'entry'][u'author'][0][u'name'][u'$t']
    except:
        print '\tNo uploader name'

    try:
        returnData['authorId']=videoData[u'entry'][u'author'][0][u'yt$userId'][u'$t']
    except:
        print '\tNo uploader id'

    try:
        returnData['title']=videoData[u'entry'][u'title'][u'$t']
    except:
        print '\tNo title'

    try:
        returnData['uploaded']=videoData[u'entry'][u'media$group'][u'yt$uploaded'][u'$t']
        returnData['uploadedISO']=datetime.datetime.strptime(returnData['uploaded'],'%Y-%m-%dT%H:%M:%S.000Z')
    except:
        print '\tNo time of uploading'

    try:
        returnData['duration']=int(videoData[u'entry'][u'media$group'][u'yt$duration'][u'seconds'])
    except:
        print '\tNo duration'

    try:
        returnData['permissions']=videoData[u'entry'][u'yt$accessControl'][0]
    except:
        print '\tNo permissions'
    '''
    if 'permissions' in returnData.keys():
        try:
        returnData['permissions'].append(videoData[u'entry']['yt$private'])
    '''
    return returnData

############
def getVideoData(vid):
############
    '''Takes vide ID (str) and gets full video info from API.'''
    requestUrl='https://gdata.youtube.com/feeds/api/videos/'+vid+'?v=2&alt=json'
    d=requests.get(requestUrl)
  
    nTries=0

    while not d.status_code==200:
        print d.text
    
        if re.search(r'too_many_recent_calls|ServiceUnavailableException',d.text):
            print 'API THRASHED. SLEEPING...'
            time.sleep(60)
            print 'RETRYING'
            d=requests.get(requestUrl)
            print 'GOT CODE',d.status_code
            nTries+=1

            if nTries==10 or re.search('Video not found|Private video',d.text):
                print 'GIVING UP'
                return {'videoId':vid,'missing':[int(time.time())]}
    return d.json()
###########
def main():
###########
    '''Takes keyword as search term and queries API
    for videos uploaded in last 24 hours in hourly 
    increments'''
    global QUERY
    global nVideos
    global nComments

    now=datetime.datetime.now()

    today=date(now.year,now.month,now.day)
  # Throw away hour, minute, second
  
    today=today-datetime.timedelta(days=diff)
  # Look back diff days

    yesterday=today-datetime.timedelta(days=1)

    todayDate=today.strftime("%Y-%m-%dT%H:%M:%SZ")
    yesterdayDate=yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")

    startDates=[yesterdayDate]
    endDates=[todayDate]

    if True:
	# Hourly increments
        startDates=[d for d in rrule(HOURLY,dtstart=yesterday,until=today-datetime.timedelta(hours=1))]
        startDates=[d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in startDates]

        startDates=startDates[0:25]
        endDates=startDates[1:26]

    for start,end in zip(startDates,endDates):

        requestString='https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key='+KEY+'&maxResults=50&type=video&publishedBefore='+end+'&publishedAfter='+start

        print 'QUERYING API IN RANGE',start,end

        d=requests.get(requestString)
        print d.status_code

        ##############
        ## Error handling
        nTries=0

        while not d.status_code==200:
            print d.text
    
            if re.search(r'too_many',d.status_code):
                print 'API THRASHED. SLEEPING...'
                time.sleep(60)
                print 'RETRYING'
                d=requests.get(requestString)
                print 'GOT CODE',d.status_code
                nTries+=1

                if nTries==10:
                    print 'GIVING UP'
                    sys.exit(1)
  ###############
    
        data=d.json()
        data['retrieved']=[time.localtime()]
        videoIds=[]

        print 'FOUND',len(data['items']),'RESULTS'

        for v,video in enumerate(data['items']):
#      print v,video
#      sys.exit(1)
#    print video[u'id']
            videoId=video[u'id']['videoId']
            videoIds.append(videoId)

            videoData=getVideoData(videoId)

            print videoId
            print '\t',videoData.keys()
            print ''
            finalVideoData=getUsefulParts(videoData,videoId)

            putInMongo(finalVideoData)

    ##
    ## Get comments here
            nVideos+=1
        print 'GOT ALL VIDEOS',nVideos
        print 'GETTING COMMENTS...'
        for v in videoIds:
            putCommentsInMongo(v)

        print 'GOT ALL COMMENTS',nComments
#########################
if __name__=='__main__':
  main()
