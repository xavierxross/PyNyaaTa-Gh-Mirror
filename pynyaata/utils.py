import re
from datetime import datetime

from dateparser import parse

from .config import MYSQL_ENABLED, BLACKLIST_WORDS


def link_exist_in_db(href):
    if MYSQL_ENABLED:
        from .models import AnimeLink
        return AnimeLink.query.filter_by(link=href).first()
    return False


def parse_date(str_to_parse, date_format=''):
    if str_to_parse is None:
        return datetime.fromtimestamp(0)
    elif isinstance(str_to_parse, datetime):
        return str_to_parse
    else:
        date = parse(str_to_parse, date_formats=[date_format])
        if date:
            return date
        else:
            return datetime.fromtimestamp(0)


def boldify(str_to_replace, keyword):
    if keyword:
        return re.sub('(%s)' % keyword, r'<b>\1</b>', str_to_replace, flags=re.IGNORECASE)
    else:
        return str_to_replace


def clean_model(obj):
    for attr in dir(obj):
        if not attr.startswith('_') and getattr(obj, attr) is None:
            try:
                setattr(obj, attr, '')
            except AttributeError:
                pass
    return obj


def check_blacklist_words(url):
    return any(word.lower() in url.lower() for word in BLACKLIST_WORDS)
