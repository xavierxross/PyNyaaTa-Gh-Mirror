from logging import getLogger
from time import sleep

from pynyaata.config import app, APP_PORT, IS_DEBUG

while True:
    try:
        app.run('0.0.0.0', APP_PORT, IS_DEBUG)
    except Exception as e:
        getLogger().exception(e)
        sleep(10)
        pass
