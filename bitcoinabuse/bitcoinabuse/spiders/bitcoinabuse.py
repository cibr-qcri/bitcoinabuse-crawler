import datetime
import re
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup
from w3lib.html import remove_tags

from ..items import BitcoinabuseItem


class BitcoinAbuseCrawler(scrapy.Spider):
    name = "bitcoinabuse"
    allowed_domains = ["bitcoinabuse.com"]
    start_urls = ['https://www.bitcoinabuse.com/reports']
    label_map = dict()
    last_record = 0
    report_count = dict()
    epoch = datetime.fromtimestamp(0)

    @staticmethod
    def process_token(value):
        return remove_tags(value.extract()).strip('\r\t\n')

    @staticmethod
    def decode_email(e):
        de = ""
        k = int(e[:2], 16)
        for i in range(2, len(e) - 1, 2):
            de += chr(int(e[i:i + 2], 16) ^ k)
        return de

    def handle_error(self, err):
        pass

    def parse_service(self, response):
        address = response.meta["address"]
        bs = BeautifulSoup(response.body, features="lxml")
        records = bs.find_all(lambda tag: tag.name == 'table')[-1].find_all(lambda tag: tag.name == 'td')
        record_count = len(records)

        if address not in self.report_count:
            self.report_count[address] = 0

        if "is_landing" in response.meta or self.report_count[address] < (record_count / 4):
            pages = response.xpath('/html//ul[@class = "pagination"]//li')
            if "page" not in response.url and pages:
                page_count = int(self.process_token(pages[-2]))
                for page in range(1, page_count):
                    url = "{}?page={}".format(response.url, page + 1)
                    yield scrapy.Request(url, meta={"address": address, "is_landing": True}, dont_filter=True,
                                         callback=self.parse_service, errback=self.handle_error)

            soup = BeautifulSoup(response.text, "lxml")
            title = soup.title.string.strip() if soup.title else ""

            if "is_landing" not in response.meta:
                record_count -= (self.report_count[address] * 4)
                self.report_count[address] += (record_count / 4)
            for i in range(0, record_count, 4):
                input_date = datetime.strptime(records[i].text.strip(), "%b %d, %Y").date()
                timestamp = datetime.combine(input_date, datetime.min.time()).timestamp() * 1000

                item = BitcoinabuseItem()
                item['timestamp'] = timestamp
                item['abuse_type'] = records[i + 1].text.strip()
                abuser = records[i + 2].text
                if records[i + 2].find('a') and records[i + 2].find('a')['data-cfemail']:
                    decrypted_email = self.decode_email(records[i + 2].find('a')['data-cfemail'])
                    abuser = abuser + " " + decrypted_email
                regex = r'[^\[\]]+(?=\])'
                item["abuser"] = re.sub(regex, '', abuser).replace('[', '').replace(']', '').strip()
                item["description"] = records[i + 3].text
                item["address"] = address
                item["url"] = response.url
                item["title"] = title
                item["response"] = response.text
                yield item

        url = "https://www.bitcoinabuse.com/reports?page={}".format(1)
        yield scrapy.Request(url, meta={"type": "page", "loop": True}, callback=self.parse, dont_filter=True)

    def parse(self, response):
        pages = response.xpath('/html//ul[@class = "pagination"]//li')
        page_count = int(self.process_token(pages[-2]))

        if "type" in response.meta and response.meta["type"] == "page":
            addresses = response.xpath('/html//div[@class = "container"]//div[@class = "row"][position()=2]'
                                       '//div//a/@href')
            for address in addresses:
                btc_address = address.get().split('/')[-1].strip()
                url = "https://www.bitcoinabuse.com{}".format(address.get())
                yield scrapy.Request(url, meta={"address": btc_address}, dont_filter=True,
                                     callback=self.parse_service, errback=self.handle_error)
        else:
            for page in range(page_count):
                url = "https://www.bitcoinabuse.com/reports?page={}".format(page + 1)
                yield scrapy.Request(url, meta={"type": "page"}, dont_filter=False)
