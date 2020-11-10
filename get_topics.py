import gensim
from pymongo import MongoClient

# Set up mongodb client
client = MongoClient()
db = client.yt_db


class dummyCorpus(object):
    def __iter__(self):
        for d in db.TOPIC_STRINGS.find({}, {'_id': 0, 'doc': 1}):
            yield gensim.corpora.dictionary.doc2bow(d['doc'].split(' '))


class documents(object):
    def __iter__(self):
        for d in db.TOPIC_STRINGS.find({}, {'_id': 0, 'doc': 1}):
            yield d['doc'].split(' ')


def getWord2Vec():
    docs = documents()
    model = gensim.models.Word2Vec(docs, min_count=1)
    return model


def main():
    n = 0


if __name__ == '__main__':
    main()
