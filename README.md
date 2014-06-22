#Summary
This is a 

#Dependencies
##Python
* [requests](http://docs.python-requests.org/en/latest/)
* [Flask](http://flask.pocoo.org/)
* [PyMongo](http://api.mongodb.org/python/2.7rc0/)
##Other
* [MongoDB](http://www.mongodb.org/)
* [Jinja](http://jinja.pocoo.org/docs/)
* [jQuery](http://jquery.com/)
* [D3](http://d3js.org/)
* Requires a YouTube Public [API key](https://developers.google.com/youtube/)

#Example Usage
Ideal setup sets up a series of [cron jobs](http://www.adminschoice.com/crontab-quick-reference/) to run each day to grab videos from the previous day (using `get_yesterdays_videos.py`) matching a set of keywords to be placed in a MongoDB. At the end of each day also perform some maintenance to check if previous days videos have been removed (`check_videos_exist.py`), to grab new comments on old videos (`update_video_comments.py`).

```
1 17 * * * /usr/bin/python <path>get_yesterdays_videos.py -q <query> >> <path>/log/out_<query>_$(date +\%d_\%m_\%Y).out 2>><path>/log/out_<query>_$(date +\%d_\%m_\%Y).err
 
1 18 * * * /usr/bin/python <path>/makeViewsInt.py >> <path>/log/out_int_$(date +\%d_\%m_\%Y).out 2>><path>/log/out_int_$(date +\%d_\%m_\%Y).err
1 19 * * * /usr/bin/python <path>/check_videos_exist.py  >> <path>/log/out_exist_$(date +\%d_\%m_\%Y).out 2>><path>/log/out_exist_$(date +\%d_\%m_\%Y).err
1 20 * * * /usr/bin/python <path>/update_video_comments.py >> <path>/log/out_update_$(date +\%d_\%m_\%Y).out 2>><path>/log/out_update_$(date +\%d_\%m_\%Y).err
```
