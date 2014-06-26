import gensim
import sys,re

from pymongo import MongoClient
client = MongoClient()
db=client.yt_db
# Set up mongodb client

############
class documents(object):
############
#    def __init__(self):
#        return self

    def __iter__(self):
        for d in db.TOPIC_STRINGS.find({},{'_id':0,'doc':1}):
            yield d['doc'].split(' ')

############
def getWord2Vec():
############
    docs=documents()
    model = gensim.models.Word2Vec(docs,min_count=1)

    return model

############
def main():
############
    model=getWord2Vec()

    n=0
    '''
    for d in documents:
        print d

        n+=1
        if n==10:sys.exit(1)
    '''

if __name__=='__main__':
    main()
