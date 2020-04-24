from .animeultime import AnimeUltime
from .core import Other
from .nyaa import Nyaa
from .pantsu import Pantsu
from .yggtorrent import YggTorrent, YggAnimation


def run_all(*args, **kwargs):
    return [
        Nyaa(*args, **kwargs).run(),
        Pantsu(*args, **kwargs).run(),
        YggTorrent(*args, **kwargs).run(),
        YggAnimation(*args, **kwargs).run(),
        AnimeUltime(*args, **kwargs).run(),
    ]


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
