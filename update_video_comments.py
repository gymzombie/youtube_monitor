'''Script to be called periodically to cycle through videos
in DB and see if there are any new comments, or if previous 
comments removed. Cycles through videos in reverse order by
last update time.'''
from get_yesterdays_videos import *
import sys


###########
def main():
    ###########
    restartId = -999

    if len(sys.argv) > 1:
        restartId = sys.argv[1]
        print('RESTARTING AT', restartId)

    nVids = 0

    #  for v in db.VIDEOS.find({}).batch_size(20):
    for v in db.VIDEOS.find({}).sort('retrieved.-1', 1):
        if restartId == -999 or (not restartId == -999 and restartId == v['videoId']):
            print(v['videoId'], '------', v['retrieved'][-1])
        # If not been checked for 12 hours
        # if now()-v.retrieved.-1>12*60*60
        putCommentsInMongo(v['videoId'])
        nVids += 1
        restartId = -999
    print('CYCLED THROUGH', nVids, 'VIDEOS')


if __name__ == '__main__':
    main()
