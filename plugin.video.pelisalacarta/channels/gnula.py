# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Shurweb
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "gnula"
__category__ = "F"
__type__ = "generic"
__title__ = "Gnula"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.gnula mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Estrenos"      , action="peliculas"    , url="http://gnula.nu/peliculas-online/lista-de-peliculas-online-parte-1/"))
    itemlist.append( Item(channel=__channel__, title="Generos"       , action="generos"   , url="http://gnula.nu/generos/lista-de-generos/"))
    itemlist.append( Item(channel=__channel__, title="Recomendadas"  , action="peliculas"   , url="http://gnula.nu/peliculas-online/lista-de-peliculas-recomendadas/"))
    #itemlist.append( Item(channel=__channel__, title="Portada"       , action="portada"    , url="http://gnula.nu/"))
    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.gnula generos")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    # <span style="font-weight: bold;">Lista de géneros</span><br/>
    data = scrapertools.find_single_match(data,'<spa[^>]+>Lista de g(.*?)/table')

    # <strong>Historia antigua</strong> [<a href="http://gnula.nu/generos/lista-de-peliculas-del-genero-historia-antigua/"
    patron = '<strong>([^<]+)</strong> .<a href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    for genero,scrapedurl in matches:
        title =  scrapertools.htmlclean(genero)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action='peliculas', title=title , url=url , thumbnail=thumbnail , plot=plot , extra=title) )
    
    itemlist = sorted(itemlist, key=lambda item: item.title)

    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.channels.gnula peliculas")

    '''
    <a class="Ntooltip" href="http://gnula.nu/comedia-romantica/ver-with-this-ring-2015-online/">With This Ring<span><br/>
    <img src="http://gnula.nu/wp-content/uploads/2015/06/With_This_Ring2.gif"></span></a> [<span style="color: #33ccff;">18/07/15</span> <span style="color: #33ff33;">(VS)</span><span style="color: red;">(VC)</span><span style="color: #cc66cc;">(VL)</span>] [<span style="color: #ffcc99;">HD-R</span>]&#8212;&#8211;<strong>Comedia, Romántica</strong><br/>
    '''
    '''
    <a class="Ntooltip" href="http://gnula.nu/aventuras/ver-las-aventuras-de-tintin-el-secreto-del-unicornio-2011-online/">The Adventures of Tintin<span><br />
    <img src="http://gnula.nu/wp-content/uploads/2015/07/The_Adventures_of_Tintin_Secret_of_the_Unicorn2.gif"></span></a> (2011) [<span style="color: #33ccff;">10/07/15</span> <span style="color: #33ff33;">(VS)</span><span style="color: red;">(VC)</span><span style="color: #cc66cc;">(VL)</span>] [<span style="color: #ffcc99;">DVD-R</span>]&#8212;&#8211;<strong>Animación, Infantil, Aventuras</strong><br />
    '''
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron  = '<a class="Ntooltip" href="([^"]+)">([^<]+)<span><br[^<]+'
    patron += '<img src="([^"]+)"></span></a>(.*?)<br'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for scrapedurl,scrapedtitle,scrapedthumbnail,resto in matches:
        plot = scrapertools.htmlclean(resto).strip()
        title = scrapedtitle+" "+plot
        fulltitle = title
        contentTitle = title
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action='findvideos', title=title , fulltitle=fulltitle , url=url , thumbnail=thumbnail , plot=plot , viewmode="movie", extra=title, hasContentDetails="true", contentTitle=contentTitle, contentThumbnail=thumbnail) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.zpeliculas gnula item="+item.tostring())

    # Descarga la página para obtener el argumento
    data = scrapertools.cachePage(item.url)
    item.plot = scrapertools.find_single_match(data,'<div class="entry">(.*?)<div class="iframes">')
    item.plot = scrapertools.htmlclean(item.plot).strip()
    item.contentPlot = item.plot

    newthumbnail = scrapertools.find_single_match(data,'<div class="entry"[^<]+<p align="center"><img alt="[^"]+" src="([^"]+)"')
    if newthumbnail!="":
        item.thumbnail = newthumbnail
        item.contentThumbnail = newthumbnail

    logger.info("[pelisalacarta.channels.zpeliculas findvideos plot="+item.plot)

    return servertools.find_video_items(item=item,data=data)

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    peliculas_items = peliculas(mainlist_items[0])
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = servertools.find_video_items( item=pelicula_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien