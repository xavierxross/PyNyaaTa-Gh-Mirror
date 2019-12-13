# 𝛑 😼 た
> "PyNyaaTa", Xéfir's personal animes torrent search engine

I'm lazy and I want to search across severall VF and VOSTFR torrents databases in one click.
That's the starting point that build this app.
At first, it was a crappy PHP project without any good futur.
After a good rewrite in Python, it's time to show it to the public, and here it is!

## Installing / Getting started

### With Docker

- Install Docker: https://hub.docker.com/search/?type=edition&offering=community
- Clone this repository
- Launch a terminal and move into the root of the cloned repository
- Run `docker-compose build`
- Run `docker-compose up -d`
- The app is accessible at http://localhost:5000

### Without Docker

- Install Python 3: https://www.python.org/downloads/
- Install Pip: https://pip.pypa.io/en/stable/installing/
- Install MariaDB (or any MySQL server): https://mariadb.com/downloads/
- Clone this repository
- Launch a terminal and move into the root of the cloned repository
- Run `pip install -r requirements.txt`
- Copy the `.env.dist` file to `.env` and ajust values to point to your MySQL server
- Run `python3 app.py`
- The app is accessible at http://localhost:5000

## Features

* Search on [Nyaa.si](https://nyaa.si/), [Nyaa.net (codename Pantsu)](https://nyaa.net/), [YggTorrent](https://duckduckgo.com/?q=yggtorrent) and [Anime-Ultime](http://www.anime-ultime.net/index-0-1)
* Provide useful links to [TheTVDB](https://www.thetvdb.com/), [Nautiljon](https://www.nautiljon.com/) and [AnimeMangaDDL](https://animemangaddl.com/) during a search
* Color official and bad links
* Add seeded links to a database
* Color seeded link on search
* Run a batch to list all dead link on database

## Configuration

All is managed by environment variables.
Please look into the `.env.dist` file to list all env variables possible.

## Links

- Project homepage: https://nyaa.crystalyx.net/
- Repository: https://git.crystalyx.net/Xefir/PyNyaaTa
- Issue tracker: https://git.crystalyx.net/Xefir/PyNyaaTa/issues
- My other projects: https://git.crystalyx.net/Xefir

## Licensing

```
           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                   Version 2, December 2004

Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHAT THE FUCK YOU WANT TO.
```
