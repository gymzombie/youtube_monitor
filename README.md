#Summary
This is a application to monitor YouTube activity related to a number of user defined queries. The backend queries the YouTube API at regualr intervals and stores data related to the content (video meta-data but _not_ the videos themselves, along with public user comments and user information). The front end uses Python-Flask and PyMongo to interface with this datand D3 and jQuery to serve it in a web interface.

The main features of the application are

* To monitor changing trends in different topics over time
* To provide a means to navigate this content
* To understand why and how quickly content is removed
* To allow the manual tagging of content into classes such as relevant/not relevant through crowdsourcing
* To analyse the language and topics represented in video comments

Requires a YouTube API key to be stored in `settings.py`. Data stored in a MongoDB database called `yt_db` with collections `VIDEOS`, `COMMENTS` and `AUTHORS` along with a small collection counting number of videos matching each query for convenience; `QUERIES`.

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
