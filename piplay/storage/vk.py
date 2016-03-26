import configparser
import logging
import vk
import os
import sys
from piplay.config import logging as plog

logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME)
logger = logging.getLogger(__name__)
logger.debug('VK storage connected')


class vkAPI:
    def __init__(self):
        self._api = None

    @property
    def api(self):
        if not self._api:
            self.initializeAPI()
        return self._api

    def initializeAPI(self):
        commonconfig = configparser.ConfigParser()
        try:
            with open(os.path.expanduser('~/.piplay/config'), 'r') as f:
                commonconfig.read_file(f)
        except IOError:
            logger.error("Config file for VK not found.")
        try:
            app_id = commonconfig['vk']['app_id']
            user_login = commonconfig['vk']['user_login']
            user_password = commonconfig['vk']['user_password']
            scope = 'offline, audio'
            logger.debug('Initialize VK session')
            session = vk.AuthSession(app_id=app_id, user_login=user_login, user_password=user_password, scope=scope)
            logger.debug('Initialize VK api')
            self._api = vk.API(session)
        except KeyError:
            logger.error("Can't load VK identify data. VK API won't be loaded")

call = vkAPI()


def search(request, resCountAsked):
    results = []
    logger.info('Search %s in VK', request)
    try:
        results = call.api.audio.search(
            q=request,
            count=resCountAsked,
            auto_complete=1
        )
        logger.debug('Return found results')
    except (NameError, AttributeError):
        logger.error("Can't create VK API call. Uninitialized API instance?")
    except:
        logger.error("Unexpected error happened: %s", sys.exc_info())
        sys.exit(1)

    res = []
    for result in results[1:]:
        res.append({
            'artist': result['artist'],
            'title': result['title'],
            'url': result['url']
        })
    return res
