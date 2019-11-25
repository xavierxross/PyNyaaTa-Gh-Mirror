from subprocess import run
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from sys import platform
import re
import requests
import locale


class ConnectorException(Exception):
    def __init__(self, connector_type):
        super().__init__("Error, can't grab data from %s" % connector_type)


class Connector(ABC):
    blacklist_words = ['Chris44', 'Vol.']

    def __init__(self, query):
        self.query = query

    @abstractmethod
    def get_full_search_url(self, sort_type, page, category):
        pass

    @abstractmethod
    def search(self, sort_type, page, category):
        pass

    @abstractmethod
    def get_history(self, sort_type, page, category):
        pass

    def curl_content(self, url, params={}, ajax=False):
        if isinstance(self, YggTorrent):
            try:
                qt_env = {'QT_QPA_PLATFORM': 'offscreen'} if platform is 'linux' else {}
                qt_output = run('phantomjs --cookies-file=/tmp/cookies.json delay.js "%s" 5000' % url, env=qt_env, shell=True, check=True, capture_output=True, timeout=7000)
                output = qt_output.stdout
                http_code = 200
            except Exception as e:
                output = ''
                http_code = 500
        else:
            if ajax:
                headers = {'X-Requested-With': 'XMLHttpRequest'}
            else:
                headers = {}

            if params:
                response = requests.post(url, params, timeout=10, headers=headers)
            else:
                response = requests.get(url, timeout=10, headers=headers)

            output = response.text
            http_code = response.status_code

        return {'http_code': http_code, 'output': output}

    def get_instance(self, url):
        if 'nyaa.si' in url:
            return Nyaa()
        elif 'nyaa.net' in url:
            return Pantsu()
        elif 'anime-ultime' in url:
            return AnimeUltime()
        elif 'ygg' in url:
            return YggTorrent()
        else:
            return Other()

    def get_lang(self, str_to_test):
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
    default_sort = 'size'

    def get_full_search_url(self, sort_type=default_sort, page=1, category=None):
        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (self.query, self.query, self.query, self.query)
        return '%s/?f=0&c=1_3&s=%s&o=desc&q=%s&p=%s' % (self.base_url, sort_type, to_query, page)

    def get_history(self, sort_type=default_sort, page=1, category=None):
        output = self.search(sort_type, page, category)
        return output[0]

    def search(self, sort_type=default_sort, page=1, category=None):
        data = []
        response = self.curl_content(self.get_full_search_url(sort_type, page))

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

                    data.append({
                        'lang': self.get_lang(url.string),
                        'href': '%s%s' % (self.base_url, url['href']),
                        'name': self.boldify(url.string),
                        'comment': str(urls[0]).replace('/view/', '%s%s' % (self.base_url, '/view/')) if has_comment else '',
                        'link': tds[2].decode_contents().replace('/download/', '%s%s' % (self.base_url, '/download/')),
                        'size': tds[3].string,
                        'date': '%s:00' % tds[4].string,
                        'seeds': check_seeds,
                        'leechs': tds[6].string,
                        'downloads': check_downloads,
                        'class': 'is-%s' % tr['class'][0]
                    })

            return (data, valid_trs is not len(trs))
        else:
            raise ConnectorException(self.title)
        return (data, False)


class Pantsu(Connector):
    color = 'is-info'
    title = 'Pantsu'
    favicon = 'pantsu.png'
    base_url = 'https://nyaa.net'
    default_sort = 4

    def get_full_search_url(self, sort_type=default_sort, page=1, category=None):
        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (self.query, self.query, self.query, self.query)
        return '%s/search/%s?c=3_13&order=false&q=%s&sort=%s' % (self.base_url, page, to_query, sort_type)

    def get_history(self, sort_type=default_sort, page=1, category=None):
        output = self.search(sort_type, page, category)
        return output[0]

    def search(self, sort_type=default_sort, page=1, category=None):
        data = []
        response = self.curl_content(self.get_full_search_url(sort_type, page))

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

                    data.append({
                        'lang': self.get_lang(url.string),
                        'href': '%s%s' % (self.base_url, url['href']),
                        'name': self.boldify(url.string),
                        'comment': '',
                        'link': tds[2].decode_contents().replace('icon-magnet', 'fa fa-fw fa-magnet').replace('icon-floppy', 'fa fa-fw fa-download'),
                        'size': tds[3].string,
                        'date': datetime.strptime(tds[7]['title'], '%m/%d/%Y, %I:%M:%S %p %Z+0').strftime('%Y-%m-%d %H:%M:%S'),
                        'seeds': check_seeds,
                        'leechs': tds[5].string,
                        'downloads': check_downloads,
                        'class': 'is-%s' % tr['class'][0]
                    })

            return (data, valid_trs is not len(trs))
        else:
            raise ConnectorException(self.title)
        return (data, False)


class YggTorrent(Connector):
    color = 'is-success'
    title = 'YggTorrent'
    favicon = 'yggtorrent.png'
    base_url = 'https://www2.yggtorrent.pe'
    default_sort = 'size'

    def get_full_search_url(self, sort_type=default_sort, page=1, category=None):
        if category is None:
            raise ConnectorException(self.title)

        return '%s/engine/search?do=search&order=desc&sort=%s&category=2145&sub_category=%s&name=%s&page=%s' % (self.base_url, sort_type, category, self.query, page)

    def get_history(self, sort_type=default_sort, page=1, category=None):
        if category is None:
            raise ConnectorException(self.title)

        output = self.search(sort_type, page, category)
        return output[0]

    def search(self, sort_type=default_sort, page=1, category=None):
        if category is None:
            raise ConnectorException(self.title)

        data = []
        response = self.curl_content(self.get_full_search_url(sort_type, page, category))

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

                    data.append({
                        'lang': self.get_lang(url.string),
                        'href': url['href'],
                        'name': self.boldify(url.string),
                        'comment': '<a href="%s#comm" target="_blank"><i class="fa fa-comments-o"></i>%s</a>' % (url['href'], tds[3].string),
                        'link': '<a href="%s/engine/download_torrent?id=%s"><i class="fa fa-fw fa-download"></i></a>' % (self.base_url, re.search('/(\d+)', url['href']).group(1)),
                        'size': tds[5].string,
                        'date': datetime.fromtimestamp(int(tds[4].div.string)).strftime('%Y-%m-%d %H:%M:%S'),
                        'seeds': check_seeds,
                        'leechs': tds[8].string,
                        'downloads': check_downloads,
                        'class': ''
                    })

            return (data, valid_trs is len(trs))
        else:
            raise ConnectorException(self.title)
        return (data, False)


class AnimeUltime(Connector):
    color = 'is-warning'
    title = 'Anime-Ultime'
    favicon = 'animeultime.png'
    base_url = 'http://www.anime-ultime.net'
    default_sort = 'search'

    def get_full_search_url(self, sort_type=default_sort, page=1, category=None):
        if sort_type is 'history':
            page_date = datetime.now() - timedelta((page-1)*365/12)
            from_date = page_date.strftime('%m%Y')
        else:
            from_date = ''

        return '%s/%s-0-1/%s' % (self.base_url, sort_type, from_date)

    def search(self, sort_type=default_sort, page=1, category=None):
        data = []
        response = self.curl_content(self.get_full_search_url(sort_type, page), {'search': self.query})

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

                    data.append({
                        'lang': 'jp',
                        'href': '%s/%s' % (self.base_url, url['href']),
                        'name': url.decode_contents(),
                        'type': tds[1].string
                    })
            else:
                player = html.select('div.AUVideoPlayer')
                name = html.select('h1')
                ani_type = html.select('div.titre')

                data.append({
                    'lang': 'jp',
                    'href': '%s%s' % (self.get_full_search_url('file'), player[0]['data-serie']),
                    'name': self.boldify(name[0].string),
                    'type': ani_type[0].string.replace(':', '')
                })
        else:
            raise ConnectorException(self.title)
        return (data, False)

    def get_history(self, sort_type=default_sort, page=1, category=None):
        data = []
        response = self.curl_content(self.get_full_search_url('history', page))

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

                    data.append({
                        'lang': 'jp',
                        'href': '%s%s' % (self.get_full_search_url('file'), link['href']),
                        'name': link.string,
                        'type': tds[4].string,
                        'date': release_date
                    })
        else:
            raise ConnectorException(self.title)
        return data


class Other(Connector):
    color = 'is-danger'
    title = 'Other'
    favicon = 'blank.png'

    def get_full_search_url(self, sort_type=None, page=1, category=None):
        return ''

    def search(self, sort_type=None, page=1, category=None):
        return ([], False)

    def get_history(self, sort_type, page, category):
        return []
