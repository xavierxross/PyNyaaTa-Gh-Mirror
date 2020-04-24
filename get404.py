from pynyaata.config import app
from pynyaata.connectors.core import curl_content
from pynyaata.models import AnimeLink

app.config['SQLALCHEMY_ECHO'] = False
links = AnimeLink.query.all()

for link in links:
    html = curl_content(link.link)

    if html['http_code'] != 200:
        print('(%d) %s %s : %s' % (html['http_code'], link.title.name, link.season, link.link))
    elif 'darkgray' in str(html['output']):
        print('(darkgray) %s %s : %s' % (link.title.name, link.season, link.link))
