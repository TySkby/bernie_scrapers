import logging
import requests
import sys
import time
import yaml

from abc import ABCMeta, abstractmethod
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient


class Scraper(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.configfile = "/opt/bernie/config.yml"
        self.config = self.config()
        self.db = self.mongo()

    def config(self):
        try:
            with open(self.configfile, 'r') as f:
                conf = yaml.load(f)
        except IOError:
            msg = "Could not open config file: {0}"
            logging.info(msg.format(self.configfile))
            sys.exit(1)
        else:
            return conf

    def mongo(self):
        c = self.config["mongo"]
        db = MongoClient(c["host"], c["port"])
        db.admin.authenticate(
            c["username"],
            c["password"],
            mechanism='SCRAM-SHA-1'
        )
        return db.bernie

    def get(self, url, params=None, result_format="html", retries_remaining=3):
        response = requests.get(url, params=params or {})
        if response.status_code == 200:
            if result_format in ("html", "xml"):
                return BeautifulSoup(response.text)
            elif result_format == "json":
                return response.json()

        if retries_remaining > 1:
            time.sleep(5)
            self.get(url, params, result_format, retries_remaining=retries_remaining - 1)

        msg = "Received {0} from {1} after 3 attempts."
        logging.critical(msg.format(response.status_code, response.url))

    @abstractmethod
    def go(self):
        pass
