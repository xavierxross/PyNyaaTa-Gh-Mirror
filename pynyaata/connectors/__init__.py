from asyncio import gather

from .animeultime import AnimeUltime
from .core import Other
from .nyaa import Nyaa
from .pantsu import Pantsu
from .yggtorrent import YggTorrent, YggAnimation
from ..config import CLOUDPROXY_ENDPOINT


async def run_all(*args, **kwargs):
    coroutines = [Nyaa(*args, **kwargs).run(),
                  Pantsu(*args, **kwargs).run(),
                  AnimeUltime(*args, **kwargs).run()]

    if CLOUDPROXY_ENDPOINT:
        coroutines.extend([YggTorrent(*args, **kwargs).run(),
                           YggAnimation(*args, **kwargs).run()])

    return list(await gather(*coroutines))


def get_instance(url, query=''):
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
