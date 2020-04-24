from bs4 import BeautifulSoup

from .core import ConnectorCore, ConnectorReturn, ConnectorCache, curl_content
from ..config import BLACKLIST_WORDS
from ..utils import parse_date, link_exist_in_db


class Nyaa(ConnectorCore):
    color = 'is-link'
    title = 'Nyaa'
    favicon = 'nyaa.png'
    base_url = 'https://nyaa.si'
    is_light = False

    def get_full_search_url(self):
        sort_type = 'size'
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 'id'

        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (self.query, self.query, self.query, self.query)
        return '%s/?f=0&c=1_3&s=%s&o=desc&q=%s&p=%s' % (self.base_url, sort_type, to_query, self.page)

    def get_history(self):
        self.search()

    @ConnectorCache.cache_data
    def search(self):
        response = curl_content(self.get_full_search_url())

        if response['http_code'] == 200:
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

                    url_safe = url.get_text()

                    if any(word.lower() in url_safe.lower() for word in BLACKLIST_WORDS):
                        continue

                    valid_trs = valid_trs + 1
                    href = '%s%s' % (self.base_url, url['href'])

                    self.data.append({
                        'lang': self.get_lang(url_safe),
                        'href': href,
                        'name': url_safe,
                        'comment': str(urls[0]).replace('/view/',
                                                        '%s%s' % (self.base_url, '/view/')) if has_comment else '',
                        'link': tds[2].decode_contents().replace('/download/', '%s%s' % (self.base_url, '/download/')),
                        'size': tds[3].string,
                        'date': parse_date(tds[4].string, '%Y-%m-%d %H:%M'),
                        'seeds': check_seeds,
                        'leechs': tds[6].string,
                        'downloads': check_downloads,
                        'class': self.color if link_exist_in_db(href) else 'is-%s' % tr['class'][0]
                    })

            self.on_error = False
            self.is_more = valid_trs and valid_trs is not len(trs) - 1