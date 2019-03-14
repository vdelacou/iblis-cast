from __future__ import unicode_literals
from rfeed import *
from youtube_dl import YoutubeDL
import datetime
import logging

# Use Api Gateway to call the lambda function with Lambda Proxy integration
# The parameters are :
#   - url : the url where to find the videos
#   - quality : the maximum quality for the video (default 720)
#   - count : the number of item in the RSS feed (default 5)
#   - filterTitle : display the item in the feed only if the word in filter is in the video title
# eg: ?url=XXXX&quality=XXXX&count=XXXX&filterTitle=XXXX
def getRss(event, context):

    # get the parameters from API Gateway
    playlist_url = event['queryStringParameters']['url'] # url is mandatory
    # get quality if present
    if 'quality' in event['queryStringParameters']:
        quality = event['queryStringParameters']['quality']
    else:
        quality = "720" # default quality is 720
    # get count if present
    if 'count' in event['queryStringParameters']:
        count = int(event['queryStringParameters']['count'])
    else:
        count =  5  # default item in feed is 5
    # get filterTitle if present
    if 'filterTitle' in event['queryStringParameters']:
        filterTitle = event['queryStringParameters']['filterTitle']
    else:
        filterTitle = None

    # for daylimotion you need to choose m3u8 protocol to pass the 403 error (cookies problem)
    if 'dailymotion'.upper() in playlist_url.upper():
        formatDowload = '[height<='+quality+'][protocol^=m3u8]'
    else:
        formatDowload = '([protocol=https]/[protocol=http])bestvideo+bestaudio[height<='+quality+'][ext=mp4]/best[height<='+quality+']/best' # if not found, we asked for best

    ydl_opts = {     
        # we prefer in http and mp4 or webm and we try to get the quality or lower
        'format': formatDowload,
        'playlistend': count,
        'ignoreerrors': True,
        'quiet': True,
        'youtube_include_dash_manifest': False, # make it faster by reducing network I/O
    }
    with YoutubeDL(ydl_opts) as ydl:
        # get all information from the given url
        result = ydl.extract_info(playlist_url, download=False)

    # initialize the RSS items list
    items = []
    # we use the first video thumbnail for rss feed picture
    first_thumbnail = None
    # Get first episode uploader for main feed
    first_uploader = None
    # Get first episode uploader playlist name for main feed
    first_uploader_playlist = None

    # if not a playlist we add video to an array
    video_list = []
    if 'entries' in result:
        video_list = result['entries']
    else:
        video_list = [result]   

    # we have a playlist
    for video in video_list:

        # if an error occurs, go to next video
        if not video:
            print('ERROR: Unable to get info. Continuing...')
            continue

        # get the Duration
        if video.get('duration'):
            duration = video.get('duration')
        else:
            duration = 10

        # get the Size
        video_size = 1000
        if video.get('filesize'):
            video_size = video.get('filesize')

        # we use the first video Thumbnail as the Feed Thumbnail  
        if not first_thumbnail:
            first_thumbnail = video.get('thumbnail')
        
        # get the name of the uploader of the first video
        if not first_uploader:
            if video.get('duration'):
                first_uploader = video.get('uploader')
            else:
                first_uploader = ""
        
        # if have a playlist name in the first video 
        if not first_uploader_playlist:
            if video.get('playlist'):
                first_uploader_playlist = video.get('playlist')

        # create itunes item   
        itunes_item = iTunesItem(
            author = video.get('uploader'),
            image = video.get('thumbnail'),
            duration = datetime.timedelta(seconds=duration),
            subtitle = video.get('title'),
            summary = video.get('description'))
       
        url = video.get('url')

        description = ''
        if video.get('description'):
            description = video.get('description')
        webpage_url = ''            
        if video.get('webpage_url'):
            webpage_url = video.get('webpage_url')
        upload_date = datetime.datetime.now()            
        if video.get('upload_date'):
            upload_date = datetime.datetime.strptime(video.get('upload_date'), '%Y%m%d')

        # create item
        item = Item(
            title = video.get('title'),
            link = url,
            description = description + ' ' + webpage_url,
            author = video.get('uploader'),
            guid = Guid(video.get('id')), 
            pubDate = upload_date,
            enclosure = Enclosure(url=url, length=video_size, type='video/'+video.get('ext')),
            extensions = [itunes_item])
        # add item to the list
        if not filterTitle:
            items.append(item) 
        else:
            if filterTitle.upper() in video.get('title').upper():
                items.append(item)              
        

    # create the itunes feed
    summary = playlist_url
    logging.warning(result) 
    if 'title' in result:
        summary = result['title']
    email = result['webpage_url_basename']
    if 'id' in result:
        email = result['id']

    itunes = iTunes(
        author = first_uploader,
        subtitle = first_uploader,
        summary = summary,
        image = first_thumbnail,
        categories = iTunesCategory(name = 'TV & Film'),
        owner = iTunesOwner(name = first_uploader, email = email) )

    # if have playlist name is used
    if not first_uploader_playlist:
        title = summary
    else:
        # if it's from channel, not use the playlist name
        if "Uploads from " in first_uploader_playlist:
            title = first_uploader
        else:
            title = first_uploader_playlist

    # create the main feed
    feed = Feed(
        title = title,
        link = playlist_url,
        description =  title,
        lastBuildDate = datetime.datetime.now(),
        items = items,
        extensions = [itunes])

    # return response with xml content-type
    response = {
        "statusCode": 200,
        "headers": {'Content-Type': 'text/xml'},
        "body": feed.rss()
    }

    return response
    
