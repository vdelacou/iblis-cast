from __future__ import unicode_literals
from rfeed import *
from youtube_dl import YoutubeDL
import datetime

def getRss(event, context):
    # get the parameters
    playlist_url = event['queryStringParameters']['url']
    if 'quality' in event['queryStringParameters']:
        quality = event['queryStringParameters']['quality']
    else:
        quality = "720"
    if 'count' in event['queryStringParameters']:
        count = int(event['queryStringParameters']['count'])
    else:
        count =  5

    ydl_opts = {        
        'format': '([protocol=https]/[protocol=http])bestvideo[height<='+quality+'][ext=mp4]/best[height<='+quality+']/best',
        'playlistend': count,
        'ignoreerrors': True,
        'quiet': True,
        'youtube_include_dash_manifest': False, # make it faster by reducing network I/O
    }
    with YoutubeDL(ydl_opts) as ydl:
        # get all information from the given url
        result = ydl.extract_info(playlist_url, download=False)

    # Initialize the RSS items
    items = []
    # Get first episode thumbnail for main feed picture
    first_thumbnail = None
    # Get first episode uploader for main feed
    first_uploader = None

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

        if video.get('duration'):
            duration = video.get('duration')
        else:
            duration = 0
        # create itunes item   
        itunes_item = iTunesItem(
            author = video.get('uploader'),
            image = video.get('thumbnail'),
            duration = datetime.timedelta(seconds=duration),
            subtitle = video.get('title'),
            summary = video.get('description'))
        # create item
        video_size = 0
        if video.get('filesize'):
            video_size = video.get('filesize')
        if not first_thumbnail:
            first_thumbnail = video.get('thumbnail')
        if not first_uploader:
            if video.get('duration'):
                first_uploader = video.get('uploader')
            else:
                first_uploader = ""
             
        item = Item(
            title = video.get('title'),
            link =  video.get('webpage_url'),
            description = video.get('description'),
            author = video.get('uploader'),
            guid = Guid(video.get('id')), 
            pubDate = datetime.datetime.strptime(video.get('upload_date'), '%Y%m%d'),
            enclosure = Enclosure(url=video.get('url'), length=video_size, type='video/'+video.get('ext')),
            extensions = [itunes_item])
        # add item to the list
        items.append(item)

    # Create the itunes feed 
    itunes = iTunes(
        author = first_uploader,
        subtitle = first_uploader,
        summary = result['title'],
        image = first_thumbnail,
        categories = iTunesCategory(name = 'TV & Film'),
        owner = iTunesOwner(name = first_uploader, email = result['id']) )

    feed = Feed(
        title = first_uploader,
        link = playlist_url,
        description =  result['title'],
        lastBuildDate = datetime.datetime.now(),
        items = items,
        extensions = [itunes])

    response = {
        "statusCode": 200,
        "headers": {'Content-Type': 'text/xml'},
        "body": feed.rss()
    }

    return response
    
