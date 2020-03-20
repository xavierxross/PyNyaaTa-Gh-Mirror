from config import app
from connectors import Connector
from models import AnimeLink

app.config['SQLALCHEMY_ECHO'] = False
links = AnimeLink.query.all()

for link in links:
    connect = Connector.get_instance(link.link, link.title.keyword)
    html = connect.curl_content(link.link)

    if html['http_code'] is not 200:
        print('(%d) %s %s : %s' % (html['http_code'], link.title.name, link.season, link.link))
    elif 'darkgray' in str(html['output']):
        print('(darkgray) %s %s : %s' % (link.title.name, link.season, link.link))
