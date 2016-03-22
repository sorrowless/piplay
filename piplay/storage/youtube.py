import configparser
import logging
import pafy
from apiclient.discovery import build


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-30s %(levelname)-9s %(message)s',
    filename='/tmp/spam.log')
logger = logging.getLogger(__name__)
logger.debug('YouTube storage connected')

commonconfig = configparser.ConfigParser()
commonconfig.read('config.ini')

try:
    scope = 'id,snippet'
    DEVELOPER_KEY = commonconfig['youtube']['app_key']
except KeyError:
    logger.error("Can't load YouTube identify data. YouTube API won't be loaded")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

logger.debug('Initialize YouTube session')
try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)
except NameError:
    logger.error("Can't create YouTube API call. Uninitialized API instance?")


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
