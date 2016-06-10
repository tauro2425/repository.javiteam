# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core.item import Item
from core import logger
from core import scrapertools
from servers import servertools

__channel__ = "seriesdanko"
__category__ = "S"
__type__ = "generic"
__title__ = "Seriesdanko"
__language__ = "ES"

HOST = 'http://seriesdanko.com/'
DEBUG = config.get_setting("debug")

IDIOMAS = {'es': 'Español', 'la': 'Latino', 'vos': 'VOS', 'vo': 'VO'}


def isGeneric():
    return True


def mainlist(item):
    logger.info("pelisalacarta.seriesdanko mainlist")

    itemlist = list()
    itemlist.append(Item(channel=__channel__, title="Novedades", action="novedades", url=HOST))
    itemlist.append(Item(channel=__channel__, title="Más vistas", action="mas_vistas", url=HOST))
    itemlist.append(Item(channel=__channel__, title="Listado Alfabético", action="listado_alfabetico", url=HOST))
    itemlist.append(Item(channel=__channel__, title="Todas las series", action="listado_completo", url=HOST))
    itemlist.append(Item(channel=__channel__, title="Buscar...", action="search", url=HOST))

    return itemlist


def novedades(item):
    logger.info("pelisalacarta.seriesdanko novedades")

    itemlist = list()

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    patron = '<a title="([^"]+)" href="([^"]+)".*?>'
    patron += "<img.*?src='([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl, scrapedthumb in matches:
        # patron = "^(.*?)(?:Ya Disponible|Disponible|Disponbile|disponible|\(Actualizada\))$"
        # match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        title = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(Item(channel=__channel__, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                        action="episodios", thumbnail=scrapedthumb))

    return itemlist


def mas_vistas(item):
    logger.info("pelisalacarta.seriesdanko mas_vistas")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    patron = "<div class='widget HTML' id='HTML3'.+?<div class='widget-content'>(.*?)</div>"
    data = scrapertools.get_match(data, patron)

    return series_seccion(data)


def listado_completo(item):
    logger.info("pelisalacarta.seriesdanko listado_completo")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    patron = '<div class="widget HTML" id="HTML10".+?<div class="widget-content">(.*?)</div>'
    data = scrapertools.get_match(data, patron)

    return series_seccion(data)


def series_seccion(data):
    logger.info("pelisalacarta.seriesdanko series_seccion")

    itemlist = []
    patron = "<a href='([^']+)'.*?>(.*?)</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=__channel__, action="episodios", title=scrapedtitle, show=scrapedtitle,
                             url=urlparse.urljoin(HOST, scrapedurl)))

    return itemlist


def listado_alfabetico(item):
    logger.info("pelisalacarta.seriesdanko listado_alfabetico")

    itemlist = []

    for letra in ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                  'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=__channel__, action="series_por_letra", title=letra,
                             url=urlparse.urljoin(HOST, "series.php?id={letra}".format(letra=letra))))

    return itemlist


# La página de series por letra es igual que la de buscar
def series_por_letra(item):
    return search(item, '')


def search(item, texto):
    logger.info("[pelisalacarta.seriesdanko search texto={0}".format(texto))

    if texto != "":
        item.url = urlparse.urljoin(HOST, "/pag_search.php?q1={0}".format(texto))

    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series(item):
    logger.info("pelisalacarta.seriesdanko series")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    patron = "<a href='([^']+)'[^>]+><img class='ict' src='([^']+)' alt='([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumb, scrapedtitle in matches:
        patron = "^(?:Capitulos de: )(.*?)$"
        match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        title = scrapertools.decodeHtmlentities(match[0])
        itemlist.append(Item(channel=__channel__, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                             action="episodios", show=item.show, thumbnail=scrapedthumb, plot=""))

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.seriesdanko episodios")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    data = re.sub(r"a> <img src=/assets/img/banderas/", "a><idioma>", data)
    data = re.sub(r"<img src=/assets/img/banderas/", "|", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+>\s+<", "</idioma><", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+>", "", data)

    patron = '<div id="T1".*?'
    patron += "<img src='([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)
    thumbnail = matches[0]

    patron = "<a href='([^']+)'>(.*?)</a><idioma>(.*?)</idioma>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedidioma in matches:
        idioma = ""
        for i in scrapedidioma.split("|"):
            idioma += " [" + IDIOMAS.get(i, "OVOS") + "]"
        title = scrapedtitle + idioma

        itemlist.append(Item(channel=__channel__, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                             action="findvideos", show=item.show, thumbnail=thumbnail, plot="", language=idioma))

    # Opción "Añadir esta serie a la biblioteca de XBMC"
    if config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.seriesdanko findvideos")

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)

    online = re.findall('<table class=.+? cellpadding=.+? cellspacing=.+?>(.+?)</table>', data,
                        re.MULTILINE | re.DOTALL)

    return parse_videos(item, "Ver", online[0]) + parse_videos(item, "Descargar", online[1])


def parse_videos(item, tipo, data):
    logger.info("pelisalacarta.seriesdanko parse_videos")

    itemlist = []

    pattern = "<td.+?<img src='/assets/img/banderas/([^\.]+).+?</td><td.+?>(.*?)</td><td.+?" \
              "<img src='/assets/img/servidores/([^\.]+).+?</td><td.+?href='([^']+)'.+?>.*?</a></td>" \
              "<td.+?>(.+?)</td><td.+?>(.*?)</td>"

    links = re.findall(pattern, data, re.MULTILINE | re.DOTALL)

    for language, date, server, link, uploader, quality in links:
        if quality == "":
            quality = "SD"
        title = "{tipo} en {server} [{idioma}] [{quality}] ({uploader}: {fecha})".\
            format(tipo=tipo, server=server, idioma=IDIOMAS.get(language, "OVOS"), quality=quality, uploader=uploader,
                   fecha=date)

        itemlist.append(Item(channel=__channel__, title=title, url=urlparse.urljoin(HOST, link), action="play",
                             show=item.show, language=IDIOMAS.get(language, "OVOS"), quality=quality))

    return itemlist


def play(item):
    logger.info("pelisalacarta.seriesdanko play url={0}".format(item.url))

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    #logger.info("data -- {}".format(data))

    patron = '<div id="url2"><a href="([^"]+)">.+?</a></div>'
    url = scrapertools.find_single_match(data, patron)

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.channel = __channel__

    return itemlist
