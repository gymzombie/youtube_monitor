'''Some convenience functions used in get_comments.py'''

import requests
import time
import csv
import collections

secsInHour=60*60
######
def writeDict(dictionary,fileName):
######
    file=open(fileName,'w')
    writer=csv.writer(file,delimiter='\t')
    for k,v in dictionary.items():
        writer.writerow([k,v.replace('\n','|').encode('utf-8')])
    file.close()

######
def readDict(fileName):
######
    returnDict=collections.OrderedDict()
    file=open(fileName,'r')
    reader=csv.reader(file,delimiter='\t')
    for line in reader:
        returnDict[line[0]]=line[1].decode('utf-8')
        file.close
    return returnDict

######
def getTime(startTime):
######
    diff=int(time.mktime(time.localtime())-startTime)
    hours=int(diff/(secsInHour))
    minutes=int((diff-(secsInHour*hours))/60)
    secs=diff-((hours*secsInHour)+(minutes*60))
    return time.strftime("%d %B %H:%M:%S", time.localtime())+' ('+str(hours)+':'+str(minutes)+':'+str(secs)+')'
######
def getAuthorInfo(id,logFile,startTime):
######
    '''Takes a user id and returns location and summary'''

    dRaw=None
    nError=0
    skip=False

    while not dRaw:
        try:
            dRaw=requests.get('http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json')
            logFile.writerow([getTime(startTime),'http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json'])
        except:
            print '\t\tAUTHOR INFO REQUEST FAILED'
            print '\t\t',id
            time.sleep(60)
            nError+=1
            if nError==10:
                skip=True
                break
        if not skip:
        #  while dRaw.status_code in [403,503]:
            while not dRaw.status_code in [200,201]:
                print 'TOO MANY REQUESTS OR API UNAVAILABLE! SLEEPING....',
                logFile.writerow([getTime(startTime),'API UNAVAILABLE',dRaw.status_code,dRaw.text.encode('utf-8')])
                print dRaw.status_code
                print dRaw.text
                print getTime(startTime)
                time.sleep(60)
                dRaw=requests.get('http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json')
                logFile.writerow([getTime(startTime),'http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json'])

    d=dRaw.json()

    returnString=''

    if 'author' in d['entry'].keys():
        if 'name' in d['entry']['author'][0]:
            returnString=d['entry']['author'][0]['name']['$t']

    if 'yt$location' in d['entry'].keys():
        returnString=returnString+'\n'+d['entry']['yt$location']['$t']
    else:
        returnString=returnString+'\n'+'<NO LOCATION>'

    if 'summary' in d['entry'].keys() and '$t' in d['entry']['summary'].keys():
        returnString=returnString+'\n'+d['entry']['summary']['$t']
    else:
        returnString=returnString+'<NO SUMMARY>'
    return returnString,d

#################
def putInMongo(dummyObject,db):
#################
    '''Takes object and ref to database as parameters. Returns None.'''
    if db.VIDEO.find({u"id":dummyObject[u"id"]}).count()>0:
#      it=db.QUERY.find()
#      print it.next()

#    print 'DUPLICATE' 
        db.VIDEO.update({u"id":dummyObject[u"id"]},{"$addToSet":{u"retrieved":time.time()}})
#      it=db.QUERY.find()
#      print it.next()
    else:
#    print 'ADDED FRESH'
        dummyObject['retrieved']=[time.time()]

#################
def sanitiseNames(dummyObject):
#################
    ''' Removes $ signs from keys to put in MongoDB'''
    if type(dummyObject)==dict:
        for k,v in dummyObject.items():
#      print 'INSPECTING',k
            if re.search('\$',k,re.U):
      # Replace
                dummyObject[k.replace('$','')]=v
                del dummyObject[k]
            dummyObject[k.replace('$','')]=sanitiseNames(v)
      # CLean those values
        return dummyObject

    elif type(dummyObject)==list:
    # Might be list of dictionaries
        for e in dummyObject:
            dummyObject=[sanitiseNames(e) for e in dummyObject]
        return dummyObject
    else:
  # If bottom out to list or int or string  
#    print 'BOTTOMED OUT'
        return dummyObject
    db.VIDEO.insert(dummyObject)

