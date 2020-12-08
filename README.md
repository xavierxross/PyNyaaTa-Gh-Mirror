# π 😼た
> "PyNyaaTa", Xéfir's personal animes torrent search engine

[![Build Status](https://ci.crystalyx.net/api/badges/Xefir/PyNyaaTa/status.svg)](https://ci.crystalyx.net/Xefir/PyNyaaTa)
[![Docker Hub](https://img.shields.io/docker/pulls/xefir/pynyaata)](https://hub.docker.com/r/xefir/pynyaata)

I'm lazy, and I want to search across several VF and VOSTFR torrents databases in one click.
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
- Run `pip install pynyaata`
- Run `pynyaata`
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
Please look into the `.env.dist` file to list all possible environment variables.
You have to install MariaDB (or any MySQL server) to be able to access the admin panel.

### Bypassing CloudFlare for YggTorrent

YggTorrent use CloudFlare to protect them to DDoS attacks.
This app will make abusive requests to their servers, and CloudFlare will try to detect if PyNyaaTa is a real human or not. *I think you have the answer to the question ...*
Over time, CloudFlare will ask you systematically to prouve yourself.

CloudFlare have three type of challenge to be completed (from the easiest to resolve to the hardest) :
- Pure Javascript done through [cloudscraper](https://github.com/VeNoMouS/cloudscraper) without any configurations
- CAPTCHA *(not supported but maybe soon™)*
- JavaScript and browser actions done through [CloudProxy](https://github.com/NoahCardoza/CloudProxy)

For CloudProxy, you have to have an instance running.
Please refer to the [documentation](https://github.com/NoahCardoza/CloudProxy#installation) or install it via [docker](https://github.com/NoahCardoza/CloudProxy#docker).
After that, change the `CLOUDPROXY_ENDPOINT` environnement variable to refer to your CloudProxy instance.

If you use PyNyaaTa with Docker and the `docker-compose.yml` from this repository, you don't have to do all this, it comes pre-installed.

## Links

- Project homepage: https://nyaa.crystalyx.net/
- Source repository: https://git.crystalyx.net/Xefir/PyNyaaTa
- Issue tracker: https://git.crystalyx.net/Xefir/PyNyaaTa/issues
- My other projects: https://git.crystalyx.net/Xefir
- Docker hub: https://hub.docker.com/r/xefir/pynyaata
- Donations: https://paypal.me/Xefir

