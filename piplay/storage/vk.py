import configparser
import logging
import vk

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-30s %(levelname)-9s %(message)s')
logger = logging.getLogger(__name__)
logger.debug('VK storage connected')

commonconfig = configparser.ConfigParser()
commonconfig.read('config.ini')

try:
    app_id = commonconfig['vk']['app_id']
    user_login = commonconfig['vk']['user_login']
    user_password = commonconfig['vk']['user_password']
    scope = 'offline, audio'
    logger.debug('Initialize VK session')
    session = vk.AuthSession(app_id=app_id, user_login=user_login, user_password=user_password, scope=scope)
    logger.debug('Initialize VK api')
    api = vk.API(session)
except KeyError:
    logger.error("Can't load VK identify data. VK API won't be loaded")


def search(request):
    results = []
    logger.info('Search %s in VK', request)
    try:
        results = api.audio.search(
            q=request,
            count=10,
            auto_complete=1
        )
        logger.debug('Return found results')
    except NameError:
        logger.error("Can't create VK API call. Uninitialized API instance?")

    res = []
    for result in results[1:]:
        res.append({
            'artist': result['artist'],
            'title': result['title'],
            'url': result['url']
        })
    return res
