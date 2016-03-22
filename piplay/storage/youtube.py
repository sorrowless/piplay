import configparser
import logging
import pafy
import os
from apiclient.discovery import build
from piplay.config import logging as plog


logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME)
logger = logging.getLogger(__name__)
logger.debug('YouTube storage connected')

commonconfig = configparser.ConfigParser()
try:
    with open(os.path.expanduser('~/.piplay/config'), 'r') as f:
        commonconfig.read_file(f)
except IOError:
    logger.error("Config file for YouTube not found.")
except:
    logger.error("Unexpected error happened: %s", sys.exc_info())
    sys.exit(1)

try:
    scope = 'id,snippet'
    DEVELOPER_KEY = commonconfig['youtube']['app_key']
except KeyError:
    logger.error("Can't load YouTube identify data. YouTube API won't be loaded")
except:
    import sys
    logger.error("Unexpected error happened: %s", sys.exc_info())
    sys.exit(1)

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

logger.debug('Initialize YouTube session')
try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)
except NameError:
    logger.error("Can't create YouTube API instance")


def youtube_search(query, max_results=4):
    videos = {}
    # Call the search.list method to retrieve results matching the specified
    # query term.
    try:
        search_response = youtube.search().list(
            q=query,
            part=scope,
            maxResults=max_results,
            order='relevance',
            type='video'
        ).execute()

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos[search_result["id"]["videoId"]] = search_result["snippet"]["title"]
    except NameError:
        logger.error("Can't create YouTube API call. Uninitialized API instance?")

    return videos

YOUTUBE_BASE_URL = 'https://www.youtube.com/watch?v='


def getAudiostream(videourl):
    logger.debug('Getting audio from %s', videourl)
    video = pafy.new(videourl)
    audio = video.getbestaudio()
    return audio.url


def search(request):
    logger.info('Search %s in YouTube', request)
    results = youtube_search(request, max_results=4)
    logger.debug('Return found results:')
    res = []

    for url_id, title in results.items():
        res.append({
            'artist': "",
            'title': title,
            'url': getAudiostream(YOUTUBE_BASE_URL + url_id)
        })
    return res
