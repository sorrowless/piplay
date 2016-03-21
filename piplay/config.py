import logging
from piplay.storage import vk, youtube

STORAGES = [vk, youtube]
LOGLEVEL = logging.DEBUG
LOGFORMAT = '%(asctime)s %(name)-30s %(levelname)-9s %(message)s'

