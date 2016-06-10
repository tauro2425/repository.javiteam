# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import urlparse
import re
import os
import sys

from core import channeltools
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
from channelselector import get_thumbnail_path

__channel__ = "seriesblanco"
__category__ = "F"
__type__ = "generic"
__title__ = "Series Blanco"
__language__ = "ES"

channel_xml = channeltools.get_channel_parameters(__channel__)
HOST = "http://seriesblanco.com/"
IDIOMAS = {'es': 'Español', 'la': 'Latino', 'vos': 'VOS', 'vo': 'VO', 'japovose': 'VOSE', 'jp-sub': 'VOSE'}


DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("pelisalacarta.seriesblanco mainlist")

    thumb_series = get_thumbnail("thumb_canales_series.png")
    thumb_series_az = get_thumbnail("thumb_canales_series_az.png")
    thumb_buscar = get_thumbnail("thumb_buscar.png")

    itemlist = list([])
    itemlist.append(Item(channel=__channel__, title="Series Listado Alfabetico", action="series_listado_alfabetico",
                         thumbnail=thumb_series_az))
    itemlist.append(Item(channel=__channel__, title="Todas las Series", action="series",
                         url=urlparse.urljoin(HOST, "lista_series/"), thumbnail=thumb_series))
    itemlist.append(Item(channel=__channel__, title="Buscar...", action="search", url=HOST, thumbnail=thumb_buscar))

    return itemlist


def series_listado_alfabetico(item):
    logger.info("pelisalacarta.seriesblanco series_listado_alfabetico")

    itemlist = []

    for letra in ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                  'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(Item(channel=__channel__, action="series_por_letra", title=letra,
                             url=urlparse.urljoin(HOST, "series/{0}/buscar_letra.html".format(letra.upper()))))

    return itemlist


# La página de series por letra es igual que la de buscar
def series_por_letra(item):
    return search(item, '')


def search(item, texto):
    logger.info("[pelisalacarta.seriesblanco search texto={0}".format(texto))

    itemlist = []

    if texto != "":
        item.url = urlparse.urljoin(HOST, "/search.php?q1={0}".format(texto))

    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    '''
    <div style='float:left;width: 33%;text-align:center;'>
        <a href='/serie/2561/acacias-38.html' '>
            <img class='ict' src='http://seriesblanco.com/files/uploads/2561.jpg' alt='Capitulos de: Acacias 38'
                height='184' width='120'>
        </a>
        <div style='text-align:center;line-height:20px;height:20px;'>
            <a href='/serie/2561/acacias-38.html' style='font-size: 11px;'> Acacias 38</a>
        </div>
    </div>
    '''

    patron = "<img class='ict' src='([^']+)'[^>]+></a>" \
             "<div style='text-align:center;line-height:20px;height:20px;'>" \
             "<a href='([^']+)' style='font-size: 11px;'>([^<]+)</a>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumb, scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=__channel__, title=scrapedtitle.strip(), url=urlparse.urljoin(HOST, scrapedurl),
                             action="episodios", show=scrapedtitle.strip(), thumbnail=scrapedthumb))

    try:
        return itemlist
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series(item):
    logger.info("pelisalacarta.seriesblanco series")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    patron = "<li><a href='([^']+)' title='([^']+)'>[^<]+</a></li>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    # como no viene el thumbnail en esta pagina ponemos el thumbnail generico del canal
    thumbnail = channel_xml["thumbnail"]

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(Item(channel=__channel__, title=scrapedtitle.strip(), url=urlparse.urljoin(HOST, scrapedurl),
                             action="episodios", show=scrapedtitle.strip(), thumbnail=thumbnail))

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.seriesblanco episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<Br>|<BR>|<br>|<br/>|<br />|-\s", "", data)
    data = re.sub(r"<!--.*?-->", "", data)
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")

    data = re.sub(r"a></td><td> <img src=/banderas/", "a><idioma/", data)
    data = re.sub(r"<img src=/banderas/", "|", data)
    data = re.sub(r"\s\|", "|", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+><", "/idioma><", data)
    data = re.sub(r"\.png border='\d+' height='\d+' width='\d+'[^>]+>", "", data)

    patron = "<img id='port_serie' src='([^']+)'.*?<li data-content=\"settings\"><p>(.*?)</p>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    thumbnail = ""
    plot = ""

    for scrapedthumbnail, scrapedplot in matches:
        thumbnail = scrapedthumbnail
        plot = scrapedplot

    '''
    <td>
        <a href='/serie/534/temporada-1/capitulo-00/the-big-bang-theory.html'>1x00 - Capitulo 00 </a>
    </td>
    <td>
        <img src=/banderas/vo.png border='0' height='15' width='25' />
        <img src=/banderas/vos.png border='0' height='15' width='25' />
    </td>
    '''

    patron = "<a href='([^']+)'>([^<]+)</a><idioma/([^/]+)/idioma>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedidioma in matches:
        idioma = ""
        for i in scrapedidioma.split("|"):
            idioma += " [" + IDIOMAS[i] + "]"
        title = item.title + " - " + scrapedtitle + idioma
        itemlist.append(Item(channel=__channel__, title=title, url=urlparse.urljoin(HOST, scrapedurl),
                             action="findvideos", show=item.show, thumbnail=thumbnail, plot=plot))

    if len(itemlist) == 0 and "<title>404 Not Found</title>" in data:
        itemlist.append(Item(channel=__channel__, title="la url '" + item.url +
                                                        "' parece no estar disponible en la web. Iténtalo más tarde.",
                             url=item.url, action="series"))

    # Opción "Añadir esta serie a la biblioteca de XBMC"
    if config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta serie a la biblioteca de XBMC", url=item.url,
                             action="add_serie_to_library", extra="episodios", show=item.show))

    return itemlist

def parseVideos(item, typeStr, data):
    videoPatternsStr = [
        '<tr.+?<span>(?P<date>.+?)</span>.*?banderas/(?P<language>[^\.]+).+?href="(?P<link>[^"]+).+?servidores/(?P<server>[^\.]+).*?</td>.*?<td>.*?<span>(?P<uploader>.+?)</span>.*?<span>(?P<quality>.*?)</span>.*?</tr>',
        '<tr.+?banderas/(?P<language>[^\.]+).+?<td[^>]*>(?P<date>.+?)</td>.+?href=[\'"](?P<link>[^\'"]+).+?servidores/(?P<server>[^\.]+).*?</td>.*?<td[^>]*>.*?<a[^>]+>(?P<uploader>.+?)</a>.*?</td>.*?<td[^>]*>(?P<quality>.*?)</td>.*?</tr>'
    ]

    for vPatStr in videoPatternsStr:
        vPattIter = re.compile(vPatStr, re.MULTILINE | re.DOTALL).finditer(data)

        itemlist = []

        for vMatch in vPattIter:
            vFields = vMatch.groupdict()
            quality = vFields.get("quality")
            if not quality:
                quality = "SD"

            title = "{0} en {1} [{2}] [{3}] ({4}: {5})".format(typeStr, vFields.get("server"), IDIOMAS[vFields.get("language")],
                                                                   quality, vFields.get("uploader"), vFields.get("date"))
            itemlist.append(Item(channel=__channel__, title=title, url=urlparse.urljoin(HOST, vFields.get("link")), action="play",
                                 show=item.show))

        if len(itemlist) > 0:
            return itemlist

    return []

def findvideos(item):
    logger.info("pelisalacarta.seriesblanco findvideos")

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    online = re.findall('<table class="as_gridder_table">(.+?)</table>', data, re.MULTILINE | re.DOTALL)

    if len(online) == 0:
        online = re.findall("<table class='zebra'>(.+?)<[Bb][Rr]>", data, re.MULTILINE | re.DOTALL)

    return parseVideos(item, "Ver", online[0]) + parseVideos(item, "Descargar", online[1])

def play(item):
    logger.info("pelisalacarta.channels.seriesblanco play url={0}".format(item.url))

    data = scrapertools.cache_page(item.url)

    patron = "<input type='button' value='Ver o Descargar' onclick='window.open\(\"([^\"]+)\"\);'/>"
    url = scrapertools.find_single_match(data, patron)

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.channel = __channel__

    return itemlist


def get_thumbnail(thumb_name=None):
    img_path = config.get_runtime_path() + '/resources/images/squares'
    if thumb_name:
        file_path = os.path.join(img_path, thumb_name)
        if os.path.isfile(file_path):
            thumb_path = file_path
        else:
            thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)
    else:
        thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)

    return thumb_path
