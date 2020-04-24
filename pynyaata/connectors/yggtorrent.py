import re
from datetime import datetime
from urllib.parse import quote

from bs4 import BeautifulSoup

from .core import ConnectorCore, ConnectorReturn, ConnectorCache, curl_content
from ..config import BLACKLIST_WORDS
from ..utils import parse_date, link_exist_in_db


class YggTorrent(ConnectorCore):
    color = 'is-success'
    title = 'YggTorrent'
    favicon = 'yggtorrent.png'
    base_url = 'https://www2.yggtorrent.se'
    is_light = False
    category = 2179

    def get_full_search_url(self):
        sort_type = 'size'
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 'publish_date'
        sort_page = '&page=%s' % ((self.page - 1) * 50) if self.page > 1 else ''

        return '%s/engine/search?name=%s&category=2145&sub_category=%s&do=search&order=desc&sort=%s%s' % (
            self.base_url, self.query, self.category, sort_type, sort_page
        )

    def get_history(self):
        self.search()

    @ConnectorCache.cache_data
    def search(self):
        if self.category:
            response = curl_content(self.get_full_search_url())

            if response['http_code'] == 200:
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
                        url_safe = url.get_text()

                        if any(word.lower() in url_safe.lower() for word in BLACKLIST_WORDS):
                            continue

                        valid_trs = valid_trs + 1

                        self.data.append({
                            'lang': self.get_lang(url_safe),
                            'href': url['href'],
                            'name': url_safe,
                            'comment': '<a href="%s#comm" target="_blank"><i class="fa fa-comments-o"></i>%s</a>' %
                                       (url['href'], tds[3].decode_contents()),
                            'link': '<a href="%s/engine/download_torrent?id=%s">'
                                    '<i class="fa fa-fw fa-download"></i>'
                                    '</a>' % (self.base_url, re.search(r'/(\d+)', url['href']).group(1)),
                            'size': tds[5].string,
                            'date': parse_date(datetime.fromtimestamp(int(tds[4].div.string))),
                            'seeds': check_seeds,
                            'leechs': tds[8].string,
                            'downloads': check_downloads,
                            'class': self.color if link_exist_in_db(quote(url['href'], '/+:')) else ''
                        })

                self.on_error = False
                self.is_more = valid_trs and valid_trs is not len(trs) - 1


class YggAnimation(YggTorrent):
    title = 'YggAnimation'
    category = 2178
