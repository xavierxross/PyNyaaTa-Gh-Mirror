# 𝛑 😼 た
> "PyNyaaTa", Xéfir's personal animes torrent search engine

[![Build Status](https://ci.crystalyx.net/api/badges/Xefir/PyNyaaTa/status.svg)](https://ci.crystalyx.net/Xefir/PyNyaaTa)

I'm lazy and I want to search across severall VF and VOSTFR torrents databases in one click.
That's the starting point that build this app.
At first, it was a crappy PHP project without any good future.
After a good rewrite in Python, it's time to show it to the public, and here it is!

## Installing / Getting started

### With Docker

- Install Docker: https://hub.docker.com/search/?type=edition&offering=community
- Run `docker run -p 5000 xefir/pynyaata`
- The app is accessible at http://localhost:5000

### Without Docker

- Install Python 3: https://www.python.org/downloads/
- Install Pip: https://pip.pypa.io/en/stable/installing/
- Clone this repository
- Launch a terminal and move into the root of the cloned repository
- Run `pip install -r requirements.txt`
- Run `python3 run.py`
- The app is accessible at http://localhost:5000

## Features

* Search on [Nyaa.si](https://nyaa.si/), [Nyaa.net (codename Pantsu)](https://nyaa.net/), [YggTorrent](https://duckduckgo.com/?q=yggtorrent) and [Anime-Ultime](http://www.anime-ultime.net/index-0-1)
* Provide useful links to [TheTVDB](https://www.thetvdb.com/) and [Nautiljon](https://www.nautiljon.com/) during a search
* Color official and bad links
* Add seeded links to a database
* Color seeded link on search
* Run a batch to list all dead link on database

## Configuration

All is managed by environment variables.
Please look into the `.env.dist` file to list all env variables possible.
You have to install MariaDB (or any MySQL server) to be able to access the admin panel.

## Links

- Project homepage: https://nyaa.crystalyx.net/
- Source repository: https://git.crystalyx.net/Xefir/PyNyaaTa
- Issue tracker: https://git.crystalyx.net/Xefir/PyNyaaTa/issues
- My other projects: https://git.crystalyx.net/Xefir
- Docker hub: https://hub.docker.com/r/xefir/pynyaata
- Donations: https://paypal.me/Xefir
