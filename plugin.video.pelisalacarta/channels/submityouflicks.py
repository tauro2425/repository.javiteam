# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import cookielib
import urlparse,urllib2,urllib,re
import os
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
import urllib

__channel__ = "submityouflicks"
__category__ = "F"
__type__ = "generic"
__title__ = "submityouflicks"
__language__ = "ES"
__adult__ = "true"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.submityourflicks mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos"    , title="Útimos videos" , url="http://www.submityourflicks.com/"))
    itemlist.append( Item(channel=__channel__, action="search"    , title="Buscar", url="http://www.submityourflicks.com/index.php?mode=search&q=%s&submit=Search"))
    
    return itemlist

# REALMENTE PASA LA DIRECCION DE BUSQUEDA

def search(item,texto):
    logger.info("pelisalacarta.channels.submityourflicks search")
    tecleado = texto.replace( " ", "+" )
    item.url = item.url % tecleado
    return videos(item)

# SECCION ENCARGADA DE BUSCAR

def videos(item):
    logger.info("pelisalacarta.channels.submityourflicks videos")
    itemlist = [] 

    '''
    <div class="item-block item-normal col" >
    <div class="inner-block">
    <a href="http://www.submityourflicks.com/1846642-my-hot-wife-bending-over-and-getting-her-cunt-reamed.html" title="My hot wife bending over and getting her cunt reamed..">
    <span class="image">
    <script type='text/javascript'>stat['56982c566d05c'] = 0;
    pic['56982c566d05c'] = new Array();
    pics['56982c566d05c'] = new Array(1, 1, 1, 1, 1, 1, 1, 1, 1, 1);</script>
    <img src="
    '''

    data = scrapertools.downloadpageGzip(item.url)
    patron  = '<div class="item-block[^<]+'
    patron += '<div class="inner-block[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<span class="image".*?'
    patron += '<img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:

        title = scrapedtitle
        url = scrapedurl
        thumbnail = scrapedthumbnail.replace(" ","%20")
        plot = ""

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="play" , title=title , url=url, thumbnail=thumbnail, plot=plot, folder=False, viewmode="movie"))

    next_page_url = scrapertools.find_single_match(data,"<a href='([^']+)' class=\"next\">NEXT</a>")
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="videos", title=">> Página siguiente" , url=next_page_url, folder=True) )

    return itemlist

def play(item):
    logger.info("pelisalacarta.channels.submityourflicks play")

    data = scrapertools.cache_page(item.url)
    media_url = scrapertools.find_single_match(data,"url\:\s*'([^']+)'")
    itemlist = []
    itemlist.append(Item(channel=__channel__, action="play" , title=item.title, fulltitle=item.fulltitle , url=media_url, thumbnail=item.thumbnail, plot=item.plot, show=item.title, server="directo", folder=False))

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Da por bueno el canal si alguno de los vídeos de "Ultimos videos" devuelve mirrors
    videos_items = videos(mainlist_items[0])
    
    bien = False
    for video_item in videos_items:
        play_items = play(video_item)
        if len(play_items)>0:
            return True
    
    return False