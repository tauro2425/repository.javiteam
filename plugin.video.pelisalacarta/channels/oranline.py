# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para oranline
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import urlparse
import re
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "oranline"
__category__ = "F"
__type__ = "generic"
__title__ = "oranline"
__language__ = "ES"

DEBUG = config.get_setting("debug")

host = "http://www.oranline.com/"
b_idioma = {'1.png': 'ES', '2.png': 'LAT', '3.png': 'VOS', '4.png': 'VO', 's.png': 'ESP', 'l.png': 'LAT', 'i.png':
            'ING', 'v.png': 'VOSE'}

def isGeneric():
    return True


def mainlist(item):
    logger.info("pelisalacarta.channels.oranline mainlist")

    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="menupeliculas", title="Peliculas", url=host))
    itemlist.append(Item(channel=__channel__, action="peliculas", title="Documentales",
                         url=urlparse.urljoin(host, "Pel%C3%ADculas/documentales/")))
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar..."))

    return itemlist


def menupeliculas(item):
    logger.info("pelisalacarta.channels.oranline menupeliculas")

    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="peliculas", title="Novedades",
                         url=urlparse.urljoin(host, "Pel%C3%ADculas/peliculas/")))
    itemlist.append(Item(channel=__channel__, action="letras", title="Todas por orden alfabético",
                         url=urlparse.urljoin(host, "Pel%C3%ADculas/peliculas/")))
    itemlist.append(Item(channel=__channel__, action="generos", title="Últimas por géneros",
                         url=urlparse.urljoin(host, "Pel%C3%ADculas/peliculas/")))
    itemlist.append(Item(channel=__channel__, action="idiomas", title="Últimas por idioma",
                         url=urlparse.urljoin(host, "Pel%C3%ADculas/peliculas/")))

    return itemlist


def search(item, texto):
    logger.info("pelisalacarta.channels.oranline search")
    if item.url == "":
        item.url = "http://www.oranline.com/?s="
    texto = texto.replace(" ", "+")
    item.url = item.url+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%{0}".format(line))
        return []


def peliculas(item):
    logger.info("pelisalacarta.channels.oranline peliculas")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)

    # Extrae las entradas (carpetas)
    '''
    <div class="review-box review-box-compact" style="width: 140px;">
        <!--Begin Image1-->
        <div class="post-thumbnail">
            <a href="http://www.oranline.com/pelicula/metro-manila-2013-ver-online-y-descargar-gratis/"
                title="Metro Manila (2013) Ver Online Y Descargar Gratis">
                <img src="http://www.oranline.com/wp-content/uploads/2013/10/metro-manila-140x210.jpg"
                    alt="Metro Manila (2013) Ver Online Y Descargar Gratis" />
            </a>
            <div id="mejor_calidad">
                <a href="http://www.oranline.com/pelicula/metro-manila-2013-ver-online-y-descargar-gratis/"
                    title="Metro Manila (2013) Ver Online Y Descargar Gratis">
                    <img id="espanol" src="http://www.oranline.com/wp-content/themes/reviewit/images/HD-R_calidad.png"
                        class="idiomas" alt="Metro Manila (2013) Ver Online Y Descargar Gratis" />
                </a>
                <span>HD-R</span>
            </div>
        </div>
        <!--End Image-->
        <div class="review-box-text">
            <h2>
                <a href="http://www.oranline.com/pelicula/metro-manila-2013-ver-online-y-descargar-gratis/"
                title="Metro Manila (2013) Ver Online Y Descargar Gratis">Metro Manila (2013) Ver Online...</a>
            </h2>
            <p>Sinopsis Buscando un futuro mejor, Óscar Ramírez y su familia dejan los campos de arroz del norte ...</p>
        </div>
        <div id="campos_idiomas">
            <img id="espanol" src="http://www.oranline.com/wp-content/themes/reviewit/images/s.png" class="idiomas"
                alt="" />
            <img id="latino" src="http://www.oranline.com/wp-content/themes/reviewit/images/lx.png" class="idiomas"
                alt="" />
            <img id="ingles" src="http://www.oranline.com/wp-content/themes/reviewit/images/ix.png" class="idiomas"
                alt="" />
            <img id="vose" src="http://www.oranline.com/wp-content/themes/reviewit/images/vx.png" class="idiomas"
                alt="" />
        </div>
    </div>
    <div class="clear"></div>
    '''
    patron = '<div class="review-box.*?'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<div id="mejor_calidad"[^<]+'
    patron += '<a[^<]+<img[^<]+'
    patron += '</a[^<]+'
    patron += '<span>([^<]+)</span></div[^<]+'
    patron += '</div[^<]+'
    patron += '<![^<]+'
    patron += '<div class="review-box-text"[^<]+'
    patron += '<h2[^<]+<a[^<]+</a></h2[^<]+'
    patron += '<p>([^<]+)</p[^<]+'
    patron += '</div[^<]+'
    patron += '<div id="campos_idiomas">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail, calidad, scrapedplot, scrapedidiomas in matches:
        scrapedtitle = scrapedtitle.replace("Ver Online Y Descargar Gratis", "").strip()
        scrapedtitle = scrapedtitle.replace("Ver Online Y Descargar gratis", "").strip()
        scrapedtitle = scrapedtitle.replace("Ver Online Y Descargar", "").strip()
        scrapedtitle = scrapertools.entityunescape(scrapedtitle)

        _idiomas_ = ""

        for key, value in b_idioma.iteritems():
            if key in scrapedidiomas:
                _idiomas_ += value + ", "
        if _idiomas_ != "":
            _idiomas_ = _idiomas_[:-2]

        title = "{0} ({1}) ({2})".format(scrapedtitle, calidad, _idiomas_)

        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        plot = scrapedplot.strip()
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=__channel__, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, viewmode="movies_with_plot", folder=True))

    try:
        next_page = scrapertools.get_match(data, "<a href='([^']+)'>\&rsaquo\;</a>")
        itemlist.append(Item(channel=__channel__, action="peliculas", title=">> Página siguiente",
                             url=urlparse.urljoin(item.url, next_page), folder=True))
    except:
        try:
            next_page = scrapertools.get_match(data, "<span class='current'>\d+</span><a href='([^']+)'")
            itemlist.append(Item(channel=__channel__, action="peliculas", title=">> Página siguiente",
                                 url=urlparse.urljoin(item.url, next_page), folder=True))
        except:
            pass
        pass

    return itemlist


def letras(item):
    logger.info("pelisalacarta.channels.oranline letras")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)
    data = scrapertools.get_match(data, '<div id="alphaList" align="center">(.*?)</div>')

    # Extrae las entradas
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=__channel__, action="peliculas", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, folder=True))

    return itemlist


def generos(item):
    logger.info("pelisalacarta.channels.oranline generos")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)
    # <li class="cat-item cat-item-23831"><a href="http://www.oranline.com/Películas/3d-hou/"
    # title="Ver todas las entradas archivadas en 3D-HOU">3D-HOU</a> (5)
    data = scrapertools.get_match(data, '<li class="cat-item cat-item-\d+"><a href="http://www.oranline.com/Pel.*?s'
                                        '/generos/"[^<]+</a>(.*?)</ul>')

    # Extrae las entradas
    patron = '<li class="cat-item cat-item-\d+"><a href="([^"]+)"[^>]+>([^<]+)</a>\s+\((\d+)\)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, cuantas in matches:
        title = scrapedtitle.strip()+" ("+cuantas+")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=__channel__, action="peliculas", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, folder=True))

    return itemlist

def idiomas(item):
    logger.info("pelisalacarta.channels.oranline idiomas")
    itemlist = []

    '''
    div class="widget">
        <h3>&Uacute;ltimos estrenos</h3>
        <ul>
            <li class="cat-item cat-item-84"><a href="http://www.oranline.com/Películas/castellano/"
                title="Ver todas las entradas archivadas en Castellano">Castellano</a> (585)
            </li>
            <li class="cat-item cat-item-85"><a href="http://www.oranline.com/Películas/latino/"
                title="Ver todas las entradas archivadas en Latino">Latino</a> (623)
            </li>
            <li class="cat-item cat-item-86"><a href="http://www.oranline.com/Películas/version-original/"
                title="Ver todas las entradas archivadas en Versión Original">Versión Original</a> (27)
            </li>
            <li class="cat-item cat-item-87"><a href="http://www.oranline.com/Películas/vos/"
                title="Ver todas las entradas archivadas en VOS">VOS</a> (1471)
            </li>
    '''
    # Descarga la página
    data = get_main_page(item.url)
    data = scrapertools.get_match(data, '<div class="widget"><h3>&Uacute;ltimos estrenos</h3>(.*?)</ul>')

    # Extrae las entradas
    patron = '<li class="cat-item cat-item-\d+"><a href="([^"]+)"[^>]+>([^<]+)</a>\s+\((\d+)\)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, cuantas in matches:
        title = scrapedtitle.strip()+" ("+cuantas+")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=__channel__, action="peliculas", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, folder=True))

    return itemlist

def get_main_page(url):
    logger.info("pelisalacarta.channels.oranline get_main_page")

    headers = list([])
    headers.append(["User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"])
    headers.append(["Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
    headers.append(["Accept-Language", "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
    headers.append(["Accept-Encoding", "gzip, deflate"])

    # Descarga la página
    data = scrapertools.cachePage(url, headers=headers)
    # logger.info("pelisalacarta.channels.oranline data="+data)

    return data

def findvideos(item):
    logger.info("pelisalacarta.channels.oranline findvideos")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    '''
    <p>
    <span><img width="29" src="http://www.oranline.com/wp-content/themes/reviewit/images/1.png"></span>      
    <span>HD-Rip </span>
    <span><img src="http://www.oranline.com/wp-content/themes/reviewit/images/calidad4.png"></span>
    <span>ashley</span>
    <span><a href="#" title="HDRip - 1,63 Gb - CASTELLANO" class="tooltip"><img src="http://www.oranline.com/wp-content/themes/reviewit/images/informacion.png" width="20"></img></a> <a onclick='reportar("reportarpelicula","375879")'><img  src='http://www.oranline.com/wp-content/themes/reviewit/images/tool.png' title="reportar enlace"></img></a></span>
    <span>
    <a href="/wp-content/themes/reviewit/enlace.php?id=375879" rel="get:id=10" rev="abcwin[700,580]"><img style="width:103px" src="http://www.oranline.com/wp-content/themes/reviewit/servidores/uploaded.jpg"></img></a></span></p>
    '''
    '''
    <p>
    <span><img src="http://www.oranline.com/wp-content/themes/reviewit/images/1.png" width="25"></span>      
    <span>HD-1080 </span>
    <span><img src="http://www.oranline.com/wp-content/themes/reviewit/images/calidad5.png"></span>
    <span>Anonymous_xxx</span> 
    <span><a onclick='reportar("reportarpelicula","505001")'><img  src='http://www.oranline.com/wp-content/themes/reviewit/images/tool.png' title="reportar enlace"></img></a></span>
    <span>
    <a href="/wp-content/themes/reviewit/enlace.php?id=505001" rel="get:id=10" rev="abcwin[700,580]"><img style="width:103px" src="http://www.oranline.com/wp-content/themes/reviewit/servidores/powvideo.jpg"></img></a></span></p>
    '''
    patron  = '<p[^<]+'
    patron += '<span[^<]+<img.*?src="([^"]+)[^<]+</span[^<]+'
    patron += '<span>([^<]+)</span.*?'
    patron += 'href="([^"]+)"[^<]+<img style="[^"]+" src="([^"]+)"'
    matches2 = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches2)

    for img_idioma, calidad, scrapedurl, img_servidor in matches2:

        idioma = scrapertools.get_filename_from_url(img_idioma)

        if idioma in b_idioma.keys():
            idioma = b_idioma[idioma]

        servidor = scrapertools.get_filename_from_url(img_servidor)[:-4]

        title = "Mirror en "+servidor+" ("+idioma+") (Calidad "+calidad.strip()+")"
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG: logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))
        itemlist.append(Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, folder=True))

    return itemlist


def play(item):
    logger.info("pelisalacarta.channels.oranline play")

    data2 = scrapertools.cache_page(item.url)
    logger.info("pelisalacarta.channels.oranline data2="+data2)

    itemlist = servertools.find_video_items(data=data2)
    
    return itemlist    


# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist es "peliculas | documentales"
    mainlist_items = mainlist(Item())

    # peliculas es "novedades | alfabetco | generos | idiomas"
    peliculas_items = peliculas(mainlist_items[0])

    # novedades es la lista de pelis
    novedades_items = novedades(peliculas_items[0])
    bien = False
    for novedad_item in novedades_items:
        # mirrors es una lista de alternativas
        mirrors_items = mirrors(novedad_item)

        for mirror_item in mirrors_items:
            # videos con "play"
            videos = findvideos(mirror_item)
            for video in videos:
                enlaces = play(video)
                if len(enlaces) > 0:
                    return True

    return False
