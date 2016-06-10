# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Pelisxporno
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools


__channel__ = "pelisxporno"
__category__ = "X"
__type__ = "generic"
__title__ = "Pelisxporno"
__language__ = "ES"


DEBUG = config.get_setting("debug")
    
def isGeneric():
    return True

def mainlist(item):
    logger.info("[Pelisxporno.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Novedades" , url="http://www.pelisxporno.com/?order=date" ) )
    itemlist.append( Item(channel=__channel__, action="categorias"  , title="Categorías" , url="http://www.pelisxporno.com" ) )

    return itemlist


def lista(item):
    logger.info("[Pelisxporno.py] lista")
    itemlist = []

    # Descarga la pagina  
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)
                        
    patronvideos ='<div class="thumb">\n.*?<a href="([^"]+)" title="([^"]+)">.*?<img src="([^"]+)".*?\/>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = match[1]
        #scrapedtitle = scrapedtitle.replace("&#8211;","-")
        #scrapedtitle = scrapedtitle.replace("&#8217;","'")
        scrapedurl = match[0]
        scrapedthumbnail = match[2]
        #scrapedplot = match[0]  
        #if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        #scrapedplot=strip_tags(scrapedplot)
        itemlist.append( Item(channel=__channel__, action="detail", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot="" , folder=True) )
 
    #Extrae la marca de siguiente página

    patronvideos ='<a class="page larger" href="([^"]+)">([^"]+)<\/a>'
    matches2 = re.compile(patronvideos,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    
 
    scrapedurl = matches2[0][0]
    page = matches2[0][1]
    itemlist.append( Item(channel=__channel__, action="lista", title="Página " + page , url=scrapedurl , plot="" , folder=True) )

    return itemlist

def categorias(item):
    logger.info("[Pelisxporno.py] categorias")
    itemlist = []

    # Descarga la pagina  
    data = scrapertools.downloadpageGzip(item.url)

    # Extrae las entradas (carpetas)
    bloque_cat = scrapertools.find_single_match(data, '<li id="categories-2"(.*?)</ul>')
    logger.info("[Pelisxporno.py] "+ bloque_cat)
    patronvideos ='<a href="([^"]+)" >(.*?)</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(bloque_cat)

    for scrapedurl, scrapedtitle in matches:
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        itemlist.append( Item(channel=__channel__, action="lista", title=scrapedtitle , url=scrapedurl , folder=True) )

    return itemlist

def detail(item):
    logger.info("[Pelisxporno.py] detail")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.downloadpageGzip(item.url)

    # Busca los enlaces a los videos de los servidores
    video_itemlist = servertools.find_video_items(data=data)
    for video_item in video_itemlist:
        itemlist.append( Item(channel=__channel__ , action="play" , server=video_item.server, title=video_item.title, url=video_item.url, thumbnail=item.thumbnail, plot=item.plot, folder=False))

    return itemlist