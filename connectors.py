import locale
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from subprocess import run
from sys import platform

import requests
from bs4 import BeautifulSoup


class ConnectorReturn(Enum):
    SEARCH = 1
    HISTORY = 2


class Connector(ABC):
    blacklist_words = ['Chris44', 'Vol.']

    def __init__(self, query, page=1, return_type=ConnectorReturn.SEARCH, category=None):
        self.query = query
        self.category = category
        self.data = []
        self.is_more = False
        self.on_error = False
        self.page = page
        self.return_type = return_type

    @abstractmethod
    def get_full_search_url(self):
        pass

    @abstractmethod
    def __search(self):
        pass

    @abstractmethod
    def __get_history(self):
        pass

    def run(self):
        if not len(self.data):
            if self.return_type is ConnectorReturn.SEARCH:
                self.__search()
            elif self.return_type is ConnectorReturn.HISTORY:
                self.__get_history()
        return self

    def curl_content(self, url, params=None, ajax=False):
        if isinstance(self, YggTorrent):
            try:
                qt_env = {'QT_QPA_PLATFORM': 'offscreen'} if platform is 'linux' else {}
                qt_output = run('phantomjs --cookies-file=/tmp/cookies.json delay.js "%s" 5000' % url, env=qt_env,
                                shell=True, check=True, capture_output=True, timeout=7000)
                output = qt_output.stdout
                http_code = 200
            except Exception as e:
                output = ''
                http_code = 500
                print(e)
        else:
            if ajax:
                headers = {'X-Requested-With': 'XMLHttpRequest'}
            else:
                headers = {}

            if params is not None:
                response = requests.post(url, params, timeout=10, headers=headers)
            else:
                response = requests.get(url, timeout=10, headers=headers)

            output = response.text
            http_code = response.status_code

        return {'http_code': http_code, 'output': output}

    @staticmethod
    def get_instance(url, query):
        if 'nyaa.si' in url:
            return Nyaa(query)
        elif 'nyaa.net' in url:
            return Pantsu(query)
        elif 'anime-ultime' in url:
            return AnimeUltime(query)
        elif 'ygg' in url:
            return YggTorrent(query)
        else:
            return Other(query)

    @staticmethod
    def get_lang(str_to_test):
        if re.search('(vf|multi|french)', str_to_test, re.IGNORECASE):
            return 'fr'
        else:
            return 'jp'

    def boldify(self, str_to_replace):
        if self.query:
            return re.sub('(%s)' % self.query, r'<b>\1</b>', str_to_replace, flags=re.IGNORECASE)
        else:
            return str_to_replace


class Nyaa(Connector):
    color = 'is-link'
    title = 'Nyaa'
    favicon = 'nyaa.png'
    base_url = 'https://nyaa.si'

    def get_full_search_url(self):
        sort_type = 'size'
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 'date'

        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (self.query, self.query, self.query, self.query)
        return '%s/?f=0&c=1_3&s=%s&o=desc&q=%s&p=%s' % (self.base_url, sort_type, to_query, self.page)

    def __get_history(self):
        self.__search()

    def __search(self):
        response = self.curl_content(self.get_full_search_url())

        if response['http_code'] is 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            trs = html.select('table.torrent-list tr')
            valid_trs = 0

            for i, tr in enumerate(trs):
                if not i:
                    continue

                tds = tr.findAll('td')
                check_downloads = int(tds[7].string)
                check_seeds = int(tds[5].string)

                if check_downloads or check_seeds:
                    urls = tds[1].findAll('a')

                    if len(urls) > 1:
                        url = urls[1]
                        has_comment = True
                    else:
                        url = urls[0]
                        has_comment = False

                    if any(url.string in word for word in self.blacklist_words):
                        continue

                    valid_trs = valid_trs + 1

                    self.data.append({
                        'lang': self.get_lang(url.string),
                        'href': '%s%s' % (self.base_url, url['href']),
                        'name': self.boldify(url.string),
                        'comment': str(urls[0]).replace('/view/',
                                                        '%s%s' % (self.base_url, '/view/')) if has_comment else '',
                        'link': tds[2].decode_contents().replace('/download/', '%s%s' % (self.base_url, '/download/')),
                        'size': tds[3].string,
                        'date': '%s:00' % tds[4].string,
                        'seeds': check_seeds,
                        'leechs': tds[6].string,
                        'downloads': check_downloads,
                        'class': 'is-%s' % tr['class'][0]
                    })

            self.is_more = valid_trs is not len(trs)
        else:
            self.on_error = True


class Pantsu(Connector):
    color = 'is-info'
    title = 'Pantsu'
    favicon = 'pantsu.png'
    base_url = 'https://nyaa.net'

    def get_full_search_url(self):
        sort_type = 4
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 2

        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (self.query, self.query, self.query, self.query)
        return '%s/search/%s?c=3_13&order=false&q=%s&sort=%s' % (self.base_url, self.page, to_query, sort_type)

    def __get_history(self):
        self.__search()

    def __search(self):
        response = self.curl_content(self.get_full_search_url())

        if response['http_code'] is 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            trs = html.select('div.results tr')
            valid_trs = 0

            for i, tr in enumerate(trs):
                if not i:
                    continue

                tds = tr.findAll('td')
                check_downloads = int(tds[6].string.replace('-', '0'))
                check_seeds = int(tds[4].string.replace('-', '0'))

                if check_downloads or check_seeds:
                    url = tds[1].a

                    if any(url.string in word for word in self.blacklist_words):
                        continue

                    valid_trs = valid_trs + 1

                    self.data.append({
                        'lang': self.get_lang(url.string),
                        'href': '%s%s' % (self.base_url, url['href']),
                        'name': self.boldify(url.string),
                        'comment': '',
                        'link': tds[2].decode_contents()
                            .replace('icon-magnet', 'fa fa-fw fa-magnet')
                            .replace('icon-floppy', 'fa fa-fw fa-download'),
                        'size': tds[3].string,
                        'date': datetime
                            .strptime(tds[7]['title'], '%m/%d/%Y, %I:%M:%S %p %Z+0')
                            .strftime('%Y-%m-%d %H:%M:%S'),
                        'seeds': check_seeds,
                        'leechs': tds[5].string,
                        'downloads': check_downloads,
                        'class': 'is-%s' % tr['class'][0]
                    })

            self.is_more = valid_trs is not len(trs)
        else:
            self.on_error = True


class YggTorrent(Connector):
    color = 'is-success'
    title = 'YggTorrent'
    favicon = 'yggtorrent.png'
    base_url = 'https://www2.yggtorrent.pe'

    def get_full_search_url(self):
        sort_type = 'size'
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 'date'

        return '%s/engine/search?do=search&order=desc&sort=%s&category=2145&sub_category=%s&name=%s&page=%s' % (
            self.base_url, sort_type, self.category, self.query, self.page
        )

    def __get_history(self):
        self.__search()

    def __search(self):
        if self.category is None:
            self.on_error = True
        else:
            response = self.curl_content(self.get_full_search_url())

            if response['http_code'] is 200:
                html = BeautifulSoup(response['output'], 'html.parser')
                trs = html.select('table.table tr')
                valid_trs = 0

                for i, tr in enumerate(trs):
                    if not i:
                        continue

                    tds = tr.findAll('td')
                    check_downloads = int(tds[6].string)
                    check_seeds = int(tds[7].string)

                    if check_downloads or check_seeds:
                        url = tds[1].a

                        if any(url.string in word for word in self.blacklist_words):
                            continue

                        valid_trs = valid_trs + 1

                        self.data.append({
                            'lang': self.get_lang(url.string),
                            'href': url['href'],
                            'name': self.boldify(url.string),
                            'comment': '<a href="%s#comm" target="_blank"><i class="fa fa-comments-o"></i>%s</a>' %
                                       (url['href'], tds[3].string),
                            'link': '<a href="%s/engine/download_torrent?id=%s"><i class="fa fa-fw fa-download"></i></a>' %
                                    (self.base_url, re.search(r'/(\d+)', url['href']).group(1)),
                            'size': tds[5].string,
                            'date': datetime.fromtimestamp(int(tds[4].div.string)).strftime('%Y-%m-%d %H:%M:%S'),
                            'seeds': check_seeds,
                            'leechs': tds[8].string,
                            'downloads': check_downloads,
                            'class': ''
                        })

                self.is_more = valid_trs is not len(trs)
            else:
                self.on_error = True


class AnimeUltime(Connector):
    color = 'is-warning'
    title = 'Anime-Ultime'
    favicon = 'animeultime.png'
    base_url = 'http://www.anime-ultime.net'

    def get_full_search_url(self):
        from_date = ''
        sort_type = 'search'

        if self.return_type is ConnectorReturn.HISTORY:
            page_date = datetime.now() - timedelta((self.page - 1) * 365 / 12)
            from_date = page_date.strftime('%m%Y')
            sort_type = 'history'

        return '%s/%s-0-1/%s' % (self.base_url, sort_type, from_date)

    def __search(self):
        response = self.curl_content(self.get_full_search_url(), {'search': self.query})

        if response['http_code'] is 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            title = html.select('div.title')

            if 'Recherche' in title[0].string:
                trs = html.select('table.jtable tr')

                for i, tr in enumerate(trs):
                    if not i:
                        continue

                    tds = tr.findAll('td')

                    if len(tds) < 2:
                        continue

                    url = tds[0].a

                    self.data.append({
                        'lang': 'jp',
                        'href': '%s/%s' % (self.base_url, url['href']),
                        'name': url.decode_contents(),
                        'type': tds[1].string
                    })
            else:
                player = html.select('div.AUVideoPlayer')
                name = html.select('h1')
                ani_type = html.select('div.titre')

                self.data.append({
                    'lang': 'jp',
                    'href': '%s%s' % (self.get_file_url(), player[0]['data-serie']),
                    'name': self.boldify(name[0].string),
                    'type': ani_type[0].string.replace(':', '')
                })
        else:
            self.on_error = True

    def __get_history(self):
        response = self.curl_content(self.get_full_search_url())

        if response['http_code'] is 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            tables = html.select('table.jtable')
            h3s = html.findAll('h3')

            for i, table in enumerate(tables):
                for j, tr in enumerate(table.findAll('tr')):
                    if not j:
                        continue

                    tds = tr.findAll('td')
                    link = tds[0].a

                    current_locale = locale.getlocale()
                    locale.setlocale(locale.LC_ALL, ('fr_FR', 'UTF-8'))
                    release_date = datetime.strptime(h3s[i].string, '%A %d %B %Y : ').strftime('%Y-%m-%d %H:%M:%S')
                    locale.setlocale(locale.LC_ALL, current_locale)

                    self.data.append({
                        'lang': 'jp',
                        'href': '%s%s' % (self.get_full_search_url('file'), link['href']),
                        'name': link.string,
                        'type': tds[4].string,
                        'date': release_date
                    })


class Other(Connector):
    color = 'is-danger'
    title = 'Other'
    favicon = 'blank.png'

    def get_full_search_url(self):
        pass

    def __search(self):
        pass

    def __get_history(self):
        pass
