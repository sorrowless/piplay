import configparser
import logging
import notify2
import os
from piplay.config import logging as plog

logging.basicConfig(
    level=plog.LOGLEVEL,
    format=plog.LOGFORMAT,
    filename=plog.FILENAME)

class Notification:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification = False

        commonconfig = configparser.ConfigParser()
        try:
            with open(os.path.expanduser('~/.piplay/config'), 'r') as f:
                commonconfig.read_file(f)
        except IOError:
            self.logger.error("Common config file not found.")
        try:
            notifier = commonconfig['common']['notifications']
            if notifier == "True" or notifier == "true":
                self.notification = notify2.Notification('', '', '')
                notify2.init(__name__)
                self.logger.debug('Initialize notifier')
        except KeyError:
            self.logger.error("Can't load notify options.",
                              "Notifier won't be initialized")

    def setInfo(self, summary, message, icon):
        if self.notification:
            self.notification.summary = summary
            self.notification.message = message
            self.notification.icon = icon

    def show(self):
        if self.notification:
            self.notification.show()
