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

app_id = commonconfig['vk']['app_id']
user_login = commonconfig['vk']['user_login']
user_password = commonconfig['vk']['user_password']
scope = 'offline, audio'

logger.debug('Initialize VK session')
session = vk.AuthSession(app_id=app_id, user_login=user_login, user_password=user_password, scope=scope)
logger.debug('Initialize VK api')
api = vk.API(session)

def search(request):
    logger.info('Search %s in VK', request)
    results = api.audio.search(
        q=request,
        count=10,
        auto_complete=1
    )
    logger.debug('Return found results')

    res = []
    for result in results[1:]:
        res.append({
            'artist': result['artist'],
            'title': result['title'],
            'url': result['url']
        })
    return res