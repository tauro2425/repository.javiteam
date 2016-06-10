# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para piratestreaming
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "filmpertutti"
__category__ = "F"
__type__ = "generic"
__title__ = "filmpertutti"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.filmpertutti mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Ultimi film inseriti", action="peliculas", url="http://www.filmpertutti.co/category/film/"))
    itemlist.append( Item(channel=__channel__, title="Categorie film", action="categorias", url="http://www.filmpertutti.co"))
    itemlist.append( Item(channel=__channel__, title="Serie TV" , action="peliculas", url="http://www.filmpertutti.co/category/serie-tv/"))
    itemlist.append( Item(channel=__channel__, title="Anime Cartoon Italiani", action="peliculas", url="http://www.filmpertutti.co/category/anime-cartoon-italiani/"))
    itemlist.append( Item(channel=__channel__, title="Anime Cartoon Sub-ITA", action="peliculas", url="http://www.filmpertutti.co/category/anime-cartoon-sub-ita/"))
    itemlist.append( Item(channel=__channel__, title="Cerca...", action="search"))
    return itemlist

def categorias(item):
    itemlist = []
    
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    
    # Extrae las entradas (carpetas)
    patron  = '<a class="link-category-home" href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def search(item,texto):
    logger.info("[filmpertutti.py] "+item.url+" search "+texto)
    item.url = "http://www.filmpertutti.eu/search/"+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.filmpertutti peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    '''
    <div class="xboxcontent">
    <h2><a href="http://filmpertutti.tv/il-padrino-di-chinatown/" rel="bookmark" title="Il padrino di Chinatown" target=""><img width="192" height="262" src="http://filmpertutti.tv/wp-content/uploads/2012/06/IlpadrinodiChinatown.jpeg" class="attachment-post-thumbnail wp-post-image" alt="IlpadrinodiChinatown" title="IlpadrinodiChinatown">              Il padrino di Chinatown              </a>  </h2> 
    <p>  ...  </p>
    </div>
    '''
    '''
    div class="col-xs-6 col-sm-3 col-md-3 col-lg-2  box-container-single-image">
    <div class="general-box container-single-image">
    <a href="http://www.filmpertutti.co/barely-lethal-16-anni-e-spia-2015/" rel="bookmark" title="Link to Barely Lethal – 16 Anni e Spia (2015)" target="">
    <img width="330" height="488" src="http://www.filmpertutti.co/wp-content/uploads/2015/06/barelylethal.jpg" class="img-responsive center-block text-center wp-post-image" alt="barelylethal" />                    <h2>Barely Lethal – 16 Anni e Spia (2015)</h2>
    '''
    patron  = '<div class="general-box container-single-image"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+<h2>([^<]+)</h2>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        plot = ""
        title=scrapedtitle
        url=urlparse.urljoin(item.url,scrapedurl)
        thumbnail=urlparse.urljoin(item.url,scrapedthumbnail)
        if title.startswith("Link to "):
            title = title[8:]
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=True) )

    # Extrae el paginador
    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)" >Avanti</a>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append( Item(channel=__channel__, action="peliculas", title="Next Page >>" , url=next_page_url , folder=True) )

    return itemlist

def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los videos de "Novedades" devuelve mirrors
    novedades_items = peliculas(mainlist_items[0])
    bien = False
    for novedades_item in novedades_items:
        mirrors = servertools.find_video_items( item=novedades_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
