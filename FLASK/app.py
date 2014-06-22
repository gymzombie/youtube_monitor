#-*- coding: utf-8
'''Application to bind URLs to Python functions using the Flask framework.

Requires username/pw and host domain to be stored in settings.py
'''
from datetime import timedelta
from flask import Flask,render_template,jsonify,make_response,request,current_app,url_for
from flask.ext.pymongo import PyMongo
from flask.ext.basicauth import BasicAuth
from flask.ext.restful import Api, Resource
import flask
import traceback
from functools import update_wrapper
import collections,json,random,requests
from settings import *

app=Flask('yt_db')
api=Api(app)
app.config['BASIC_AUTH_USERNAME'] = USERNAME
app.config['BASIC_AUTH_PASSWORD'] = PASSWORD
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)
# Set up authentication
# User/pw stored in settings.py

mongo = PyMongo(app)
#######
class UserAPI(Resource):
######
  def get(self, id): 
    print 'GET'
    pass

  def put(self, id):
    print 'PUT'
    pass

  def delete(self, id):
    print 'DELETE'
    pass

####################################
def getISO(d):
  '''Convenience function to munge date'''
  iso=str(d['uploadedYear'])+'-'+str(d['uploadedMonth']).zfill(2)+'-'+str(d['uploadedDay']).zfill(2)
  return iso
####################################
def crossdomain(origin=None, methods=None, headers=None,max_age=21600, attach_to_all=True,automatic_options=True):
  if methods is not None:
    methods = ', '.join(sorted(x.upper() for x in methods))
  if headers is not None and not isinstance(headers, basestring):
    headers = ', '.join(x.upper() for x in headers)
  if not isinstance(origin, basestring):
    origin = ', '.join(origin)
  if isinstance(max_age, timedelta):
    max_age = max_age.total_seconds()
  def get_methods():
    if methods is not None:
      return methods

    options_resp = current_app.make_default_options_response()
    return options_resp.headers['allow']

  def decorator(f):
    def wrapped_function(*args, **kwargs):
      if automatic_options and request.method == 'OPTIONS':
        resp = current_app.make_default_options_response()
      else:
        resp = make_response(f(*args, **kwargs))
      if not attach_to_all and request.method != 'OPTIONS':
        return resp

      h = resp.headers

      h['Access-Control-Allow-Origin'] = origin
      h['Access-Control-Allow-Methods'] = get_methods()
      h['Access-Control-Max-Age'] = str(max_age)
      if headers is not None:
        h['Access-Control-Allow-Headers'] = headers
      return resp

    f.provide_automatic_options = False
    return update_wrapper(wrapped_function, f)
  return decorator

##################################################################
@app.route("/flask")
def hello():
  print mongo.db
  return str(mongo.db.VIDEOS.find().count())
##################################################################
@app.route("/yt/splash")
def splash():
  nVideo=mongo.db.VIDEOS.count()
  nAuthor=mongo.db.AUTHORS.count()
  nComment=mongo.db.COMMENTS.count()

  q=mongo.db.VIDEOS.aggregate([{'$match':{'query':{'$exists':'True'}}},{'$group':{'_id':{'query':'$query'},'number':{'$sum':1}}}])
  queries={}
  
  for qq in q['result']:
    queries[qq['_id']['query'][0]]=qq['number']
  for k,v in queries.items():
    print k,v
  return render_template('template6.html',queries=queries,n=(nVideo,nAuthor,nComment))
##################################################################
@app.route("/yt/explore")
def hello4():
  '''Queries DB and prepares data on video counts by query
  to be displayed using D3'''
  try: 
    v=mongo.db.VIDEOS.find().sort([('views',-1)]).limit(100)
    nVideo=mongo.db.VIDEOS.count()
    nAuthor=mongo.db.AUTHORS.count()
    nComment=mongo.db.COMMENTS.count()
    nMissing=mongo.db.VIDEOS.find({'missing':{'$exists':True}}).count()
  except:
    print traceback.print_exc()

  try:
    q=mongo.db.VIDEOS.aggregate([{'$match':{'query':{'$exists':'True'}}},{'$group':{'_id':{'query':'$query'},'number':{'$sum':1}}}])
    queries={}
  
    for qq in q['result']:
      queries[qq['_id']['query'][0]]=qq['number']
  except:
    print traceback.print_exc()

  try:
    return render_template('explore.html',videos=v,n=(nVideo,nAuthor,nComment,nMissing),queries=queries)
  except:
    print traceback.print_exc()
######################################################
@app.route("/yt/home")
def hello3():
  '''Grabs first 50 videos for display on basic homepage'''
  try: 
    v=mongo.db.VIDEOS.find().sort([('views',1)]).limit(50)
  except:
    print traceback.print_exc()
  try:
    return render_template('home.html',videos=v)
  except:
    print traceback.print_exc()
######################################################
@app.route("/count")
@crossdomain(origin='*')
def count():
  print 'COUNTING'
  try:
	  out=mongo.db.VIDEOS.aggregate([{'$match':{'uploadedISO':{'$exists':True}}},{'$project':{'uploadedDay':{'$dayOfMonth':'$uploadedISO'},'uploadedMonth':{'$month':'$uploadedISO'},'uploadedYear':{'$year':'$uploadedISO'}}},{'$group':{'_id':{'uploadedDay':'$uploadedDay','uploadedMonth':'$uploadedMonth','uploadedYear':'$uploadedYear'},'number':{'$sum':1}}},{'$sort':{'_id.uploadedMonth':1,'_id.uploadedDay':1}}])
#    out=mongo.db.VIDEOS.aggregate([{'$match':{'uploadedISO':{'$exists':True}}},{'$project':{'query':'$query','uploadedDay':{'$dayOfMonth':'$uploadedISO'},'uploadedMonth':{'$month':'$uploadedISO'},'uploadedYear':{'$year':'$uploadedISO'}}},{'$group':{'_id':{'uploadedDay':'$uploadedDay','uploadedMonth':'$uploadedMonth','uploadedYear':'$uploadedYear','query':'$query'},'number':{'$sum':1}}},{'$sort':{'_id.uploadedDay':1}}])
  except:
    print traceback.print_exc()

  outDict={}
  outList=[]
  for r in out['result']:
#    print r
    outDict[getISO(r['_id'])]=r['number']
    outList.append({'date':getISO(r['_id']),'vol':r['number']})
  try:
    jsonList=[flask.jsonify(o) for o in outList]
    jsonList=json.dumps(outList)
    print outList
    return render_template('d3_json_6.html',data=jsonList) 
#    return render_template('d3_json_2.html',data=jsonList) 
#    return render_template('d3_json_4.html',data=jsonList) 
  except:
    print traceback.print_exc()
######################################################
@app.route("/yt/query/")
def getQuery():
  param=request.args.get('q')
  try:
    print param
  except:
    print traceback.print_exc()
  return render_template('query.html',query=param)
######################################################
@app.route("/yt/randomTest",methods=['GET'])
@crossdomain(origin='*')
def getRandomTest():
  try:
    return render_template('random_test.html')
  except:
    print traceback.print_exc()
######################################################
@app.route('/yt/notrelevant/test')
def rel_test(origin='*'):
  return render_template('rel_test.html')
######################################################
@app.route('/yt/notrelevant/<string:videoId>', methods = ['PUT'])
def decrementRelevant(videoId):
  print 'DECREMENT RELEVANT'
  print videoId
  mongo.db.VIDEOS.update({'videoId':videoId},{'$inc':{'irrelevantCount':1}})
  return 'OK',200,''
######################################################
@app.route('/yt/relevant/<string:videoId>', methods = ['PUT'])
def incrementRelevant(videoId):
  print 'INCREMENTS RELEVANT'
  print videoId
  mongo.db.VIDEOS.update({'videoId':videoId},{'$inc':{'relevantCount':1}})
  return 'OK',200,''
######################################################
@app.route("/yt/random")
@crossdomain(origin='*')
def getRandom():
  coinToss1=random.random()
  coinToss2=random.random()
  if coinToss1>coinToss2:
    q=mongo.db.VIDEOS.find({'randId':{'$gt':coinToss2,'$lt':coinToss1},'missing':{'$exists':False}}).sort([('randId',1)]).limit(1)
  else:
	  q=mongo.db.VIDEOS.find({'randId':{'$gt':coinToss1,'$lt':coinToss2},'missing':{'$exists':False}}).sort([('randId',1)]).limit(1)
  v=q.next()
  del v['_id']
  try:
    return jsonify(v)
  except:
    print traceback.print_exc()
######################################################
@app.route("/yt/about")
@crossdomain(origin='*')
def getAbout():
  return render_template('about.html')
######################################################
@app.route("/yt/test_random")
def testRandom():
  try: 
    v=mongo.db.VIDEOS.find({'missing':{'$exists':False}},{'_id':False}).sort([('views',1)]).limit(50)
  except:
    print traceback.print_exc()
  videos=[vv for vv in v]
  try:
    return render_template('test_random.html',videos=videos)
  except:
    print traceback.print_exc()
######################################################
@app.route("/yt/tag")
def test():
  videos=[]
  for i in range(12):
    coinToss1=random.random()
    coinToss2=random.random()
    if coinToss1>coinToss2:
      q=mongo.db.VIDEOS.find({'randId':{'$gt':coinToss2,'$lt':coinToss1},'missing':{'$exists':False}}).sort([('randId',1)]).limit(1)
    else:
      q=mongo.db.VIDEOS.find({'randId':{'$gt':coinToss1,'$lt':coinToss2},'missing':{'$exists':False}}).sort([('randId',1)]).limit(1)
    videos.append(q.next())

  try:
    return render_template('tag.html',videos=videos)
  except:
    print traceback.print_exc()
######################################################
@app.route("/yt/totals")
@crossdomain(origin='*')
def d3plus():
  out=mongo.db.VIDEOS.aggregate([{'$match':{'uploadedISO':{'$exists':True}}},{'$project':{'query':'$query','uploadedDay':{'$dayOfMonth':'$uploadedISO'},'uploadedMonth':{'$month':'$uploadedISO'},'uploadedYear':{'$year':'$uploadedISO'}}},{'$group':{'_id':{'uploadedDay':'$uploadedDay','uploadedMonth':'$uploadedMonth','uploadedYear':'$uploadedYear','query':'$query'},'number':{'$sum':1}}},{'$sort':{'_id.uploadedMonth':1,'_id.uploadedDay':1}}])

  queries=mongo.db.QUERIES.find().sort('count',-1)
  queryList=[q['query'] for q in queries]
  queries=mongo.db.QUERIES.find().sort('count',-1)
  queryCounts=[q['count'] for q in queries]
  
  dateList=list(set([getISO(r['_id']) for r in out['result']]))
  dateList.sort()
  outList=[[] for q in queryList]
  # List of lists, one for each query

  for rr,r in enumerate(out['result']):
#    print rr,r
    try:
#      outList[dateList.index(getISO(r['_id']))][r['_id']['query'][0]]=r['number']
      qIndex=queryList.index(r['_id']['query'][0])
      outList[qIndex].append({'date':getISO(r['_id']),'value':r['number']})
    except:
      print traceback.print_exc()
  try:
    cleanedData=[json.dumps(inner) for inner in outList[0:2]]
    cleanedData=[[json.dumps(i) for i in inner] for inner in outList]
  except:
    print traceback.print_exc()
#  return render_template('totals.html',data=cleanedData,queries=queryList,queryCounts=queryCounts) 
  return render_template('totals.html',data=cleanedData,queries=queryList,queryCounts=queryCounts) 
######################################################
@app.route('/yt/map')
def map():
  D3URL=url_for('static', filename="js/d3.min.js")
  print 'URL',D3URL
  return render_template('worldmap-template.html')
######################################################
@app.route("/count2")
@crossdomain(origin='*')
def count2():
  print 'COUNTING BY QUERY'
  try:
	  out=mongo.db.VIDEOS.aggregate([{'$match':{'uploadedISO':{'$exists':True}}},{'$project':{'query':'$query','uploadedDay':{'$dayOfMonth':'$uploadedISO'},'uploadedMonth':{'$month':'$uploadedISO'},'uploadedYear':{'$year':'$uploadedISO'}}},{'$group':{'_id':{'uploadedDay':'$uploadedDay','uploadedMonth':'$uploadedMonth','uploadedYear':'$uploadedYear','query':'$query'},'number':{'$sum':1}}},{'$sort':{'_id.uploadedDay':1}}])
  except:
    print traceback.print_exc()

  outDict={}
  outList=[]
  print out['result'][0]
  lastDate=''
#  sys.exit(1)

  for r in out['result']:
    print r['_id']['query'][0],r['_id']['uploadedDay'],r['number']
    
    if not getISO(r['_id'])==lastDate:
      outList.append({'date':getISO(r['_id'])})
      lastDate=getISO(r['_id'])
    outList[-1][r[u'_id']['query'][0]]=r['number']
  print '---------------'
  for o in outList:
    print o['date']
    for k in o.keys():
      print k,
    print ''
#    outList.append({'date':getISO(r['_id']),'vol':r['number']})
  try:
    jsonList=[flask.jsonify(o) for o in outList]
    jsonList=json.dumps(outList)

    return render_template('d3_json_3.html',data=jsonList) 
  except:
    print traceback.print_exc()

######################################################
@app.route("/flask2")
def hello2():
  v=mongo.db.VIDEOS.find_one_or_404()
  if v:
    print v.keys()
    print render_template
  else:
    print 'ERR'
    return render_template('template1.html',name=None)
  return render_template('template1.html',name=v['videoId'])

if __name__=='__main__':
  app.run(DOMAIN)

