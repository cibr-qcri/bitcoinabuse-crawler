import os
from datetime import datetime
from hashlib import sha256

from elasticsearch import Elasticsearch
from scrapy.utils.project import get_project_settings


class ElasticSearchPipeline(object):
    def __init__(self):
        self.dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.settings = get_project_settings()
        self.date = datetime.today()
        self.server = self.settings['ELASTICSEARCH_CLIENT_SERVICE_HOST']
        self.port = self.settings['ELASTICSEARCH_CLIENT_SERVICE_PORT']
        self.port = int(self.port)
        self.username = self.settings['ELASTICSEARCH_USERNAME']
        self.password = self.settings['ELASTICSEARCH_PASSWORD']
        self.index = self.settings['ELASTICSEARCH_INDEX']

        if self.port:
            uri = "http://%s:%s@%s:%d" % (self.username, self.password, self.server, self.port)
        else:
            uri = "http://%s:%s@%s" % (self.username, self.password, self.server)

        self.es = Elasticsearch([uri])

    def process_item(self, item, spider):
        address = item['address']
        tag = {
            "data": {
                "timestamp": int(datetime.now().timestamp() * 1000),
                "type": "service",
                "source": "bitcoinabuse",
                "method": "html",
                "version": 1,
                "info": {
                    "domain": "www.bitcoinabuse.com",
                    "url": item["url"],
                    "title": "Bitcoin Abuse Database: {}".format(address),
                    "external_links": {
                        "href_urls": {
                            "web": [],
                            "onion": [],
                        }
                    },
                    "tags": {
                        "cryptocurrency": {
                            "address": {
                                "btc": [address]
                            }
                        },
                        "abuse": {
                            "address": address,
                            "report": {
                                "timestamp": item["timestamp"],
                                "type": item["abuse_type"],
                                "abuser": item["abuser"],
                                "description": item["description"]
                            }
                        }
                    }
                }
            }
        }
        uid = address + item["abuse_type"] + item["abuser"] + item["description"]
        self.es.index(index=self.index, id=sha256(uid.encode("utf-8")).hexdigest(), body=tag)

        return item


class FileWriterPipeline(object):

    def process_item(self, item, spider):
        uid = item["address"] + item["abuse_type"] + item["abuser"] + item["description"]
        with open("/mnt/data/{id}".format(id=uid), "w") as f:
            f.write(item["response"])

        return item
