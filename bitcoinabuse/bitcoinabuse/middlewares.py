import zlib
import random
from scrapy import signals
from scrapy.utils.gz import gunzip
from scrapy.http import Response, TextResponse
from scrapy.responsetypes import responsetypes

ACCEPTED_ENCODINGS = [b'gzip', b'deflate']
try:
    import brotli
    ACCEPTED_ENCODINGS.append(b'br')
except ImportError:
    pass


class BitcoinabuseSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BitcoinabuseDownloaderMiddleware(object):

    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(user_agent=crawler.settings.get('USER_AGENT'))
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = agent
        request.headers.setdefault('Accept-Encoding', b", ".join(ACCEPTED_ENCODINGS))

    def process_response(self, request, response, spider):
        if request.method == 'HEAD':
            return response
        if isinstance(response, Response):
            content_encoding = response.headers.getlist('Content-Encoding')
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print()
            if content_encoding:
                encoding = content_encoding.pop()
                decoded_body = self.decode(response.body, encoding.lower())
                respcls = responsetypes.from_args(
                    headers=response.headers, url=response.url, body=decoded_body
                )
                kwargs = dict(cls=respcls, body=decoded_body)
                if issubclass(respcls, TextResponse):
                    kwargs['encoding'] = None
                response = response.replace(**kwargs)
                if not content_encoding:
                    del response.headers['Content-Encoding']

        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    @staticmethod
    def decode(body, encoding):
        if encoding == b'gzip' or encoding == b'x-gzip':
            body = gunzip(body)
        if encoding == b'deflate':
            try:
                body = zlib.decompress(body)
            except zlib.error:
                body = zlib.decompress(body, -15)
        if encoding == b'br' and b'br' in ACCEPTED_ENCODINGS:
            body = brotli.decompress(body)
        return body

