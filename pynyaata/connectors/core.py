import re
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from functools import wraps
from logging import getLogger

from cloudscraper import create_scraper
from cloudscraper.exceptions import CloudflareException, reCaptchaException
from requests import RequestException

from ..config import CACHE_TIMEOUT, IS_DEBUG, REQUESTS_TIMEOUT, TWOCAPTCHA_API_KEY

scraper = create_scraper(browser={
    'custom': 'ScraperBot/1.0'
}, interpreter='js2py', recaptcha=TWOCAPTCHA_API_KEY)


class ConnectorReturn(Enum):
    SEARCH = 1
    HISTORY = 2


class ConnectorLang(Enum):
    FR = '🇫🇷'
    JP = '🇯🇵'


class Cache:
    CACHE_DATA = {}

    def cache_data(self, f):
        @wraps(f)
        def wrapper(*args, **kwds):
            connector = args[0]
            timestamp = datetime.now().timestamp()

            for connector_class in list(self.CACHE_DATA):
                for connector_func in list(self.CACHE_DATA[connector_class]):
                    for connector_query in list(self.CACHE_DATA[connector_class][connector_func]):
                        for connector_page in list(self.CACHE_DATA[connector_class][connector_func][connector_query]):
                            if self.CACHE_DATA[connector_class][connector_func][connector_query][connector_page][
                                'timeout'
                            ] < timestamp:
                                del self.CACHE_DATA[connector_class][connector_func][connector_query][connector_page]

            if connector.__class__.__name__ not in self.CACHE_DATA:
                self.CACHE_DATA[connector.__class__.__name__] = {}
            if f.__name__ not in self.CACHE_DATA[connector.__class__.__name__]:
                self.CACHE_DATA[connector.__class__.__name__][f.__name__] = {}
            if connector.query not in self.CACHE_DATA[connector.__class__.__name__][f.__name__]:
                self.CACHE_DATA[connector.__class__.__name__][f.__name__][connector.query] = {}
            if connector.page not in self.CACHE_DATA[connector.__class__.__name__][f.__name__][connector.query]:
                self.CACHE_DATA[connector.__class__.__name__][f.__name__][connector.query][connector.page] = {
                    'timeout': 0.0
                }

            cached_data = self.CACHE_DATA[connector.__class__.__name__][f.__name__][connector.query][connector.page]
            if cached_data['timeout'] > timestamp:
                connector.data = cached_data['data']
                connector.is_more = cached_data['is_more']
                connector.on_error = False
                return

            ret = f(*args, **kwds)
            if not connector.on_error:
                self.CACHE_DATA[connector.__class__.__name__][f.__name__][connector.query][connector.page] = {
                    'data': connector.data,
                    'timeout': timestamp + CACHE_TIMEOUT,
                    'is_more': connector.is_more
                }
            return ret

        return wrapper


ConnectorCache = Cache()


def curl_content(url, params=None, ajax=False):
    if ajax:
        headers = {'X-Requested-With': 'XMLHttpRequest'}
    else:
        headers = {}

    try:
        if params is not None:
            response = scraper.post(url, params, timeout=REQUESTS_TIMEOUT, headers=headers)
        else:
            response = scraper.get(url, timeout=REQUESTS_TIMEOUT, headers=headers)

        output = response.text
        http_code = response.status_code
    except (RequestException, CloudflareException, reCaptchaException) as e:
        output = ''
        http_code = 500
        if IS_DEBUG:
            getLogger().exception(e)

    return {'http_code': http_code, 'output': output}


class ConnectorCore(ABC):
    @property
    @abstractmethod
    def color(self):
        pass

    @property
    @abstractmethod
    def title(self):
        pass

    @property
    @abstractmethod
    def favicon(self):
        pass

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def is_light(self):
        pass

    def __init__(self, query, page=1, return_type=ConnectorReturn.SEARCH):
        self.query = query
        self.data = []
        self.is_more = False
        self.on_error = True
        self.page = page
        self.return_type = return_type

    @abstractmethod
    def get_full_search_url(self):
        pass

    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def get_history(self):
        pass

    @staticmethod
    def get_lang(str_to_test):
        if re.search('(vf|multi|french)', str_to_test, re.IGNORECASE):
            return ConnectorLang.FR
        else:
            return ConnectorLang.JP

    def run(self):
        if self.on_error:
            if self.return_type is ConnectorReturn.SEARCH:
                self.search()
            elif self.return_type is ConnectorReturn.HISTORY:
                self.get_history()
        return self


class Other(ConnectorCore):
    color = 'is-danger'
    title = 'Other'
    favicon = 'blank.png'
    base_url = ''
    is_light = True

    def get_full_search_url(self):
        pass

    def search(self):
        pass

    def get_history(self):
        pass
