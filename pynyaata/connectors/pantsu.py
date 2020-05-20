from bs4 import BeautifulSoup

from .core import ConnectorCore, ConnectorReturn, ConnectorCache, curl_content
from ..utils import parse_date, link_exist_in_db, check_blacklist_words


class Pantsu(ConnectorCore):
    color = 'is-info'
    title = 'Pantsu'
    favicon = 'pantsu.png'
    base_url = 'https://nyaa.net'
    is_light = False

    def get_full_search_url(self):
        sort_type = 4
        if self.return_type is ConnectorReturn.HISTORY:
            sort_type = 2

        to_query = '(%s vf)|(%s vostfr)|(%s multi)|(%s french)' % (self.query, self.query, self.query, self.query)
        return '%s/search/%s?c=3_13&order=false&q=%s&sort=%s' % (self.base_url, self.page, to_query, sort_type)

    def get_history(self):
        self.search()

    @ConnectorCache.cache_data
    def search(self):
        response = curl_content(self.get_full_search_url())

        if response['http_code'] == 200:
            html = BeautifulSoup(response['output'], 'html.parser')
            trs = html.select('div.results tr')
            valid_trs = 0

            for i, tr in enumerate(trs):
                if not i:
                    continue

                tds = tr.findAll('td')
                check_downloads = int(tds[6].get_text().replace('-', '0'))
                check_seeds = int(tds[4].get_text().replace('-', '0'))

                if check_downloads or check_seeds:
                    url = tds[1].a
                    url_safe = url.get_text()

                    if check_blacklist_words(url_safe):
                        continue

                    valid_trs = valid_trs + 1
                    href = self.base_url + url['href']

                    self.data.append({
                        'lang': self.get_lang(url_safe),
                        'href': href,
                        'name': url_safe,
                        'comment': '',
                        'link': tds[2].decode_contents().replace('icon-magnet', 'fa fa-fw fa-magnet').replace(
                            'icon-floppy', 'fa fa-fw fa-download'),
                        'size': tds[3].get_text(),
                        'date': parse_date(tds[7]['title'][:-6], '%m/%d/%Y, %I:%M:%S %p'),
                        'seeds': check_seeds,
                        'leechs': tds[5].get_text(),
                        'downloads': check_downloads,
                        'class': self.color if link_exist_in_db(href) else 'is-%s' % tr['class'][0]
                    })

            self.on_error = False
            self.is_more = valid_trs and valid_trs is not len(trs) - 1
