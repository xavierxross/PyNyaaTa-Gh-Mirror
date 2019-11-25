from connectors import AnimeUltime
from pprint import pprint

test = AnimeUltime('conan')
pprint(test.search())
