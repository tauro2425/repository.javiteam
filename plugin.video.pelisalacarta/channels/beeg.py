# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para beeg.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por aampudia
#------------------------------------------------------------

#Propiedades del Canal:
__active__ = True
__adult__ = True
__category__ = "X,F"
__changes__ = "Canal Corregido: Utilizando API"
__channel__ = "beeg"
__creationdate__ = ""
__date__ = "06/10/2015"
__language__ = "ES"
__thumbnail__ = ""
__title__ = "Beeg"
__type__ = "generic"
__version__ = 3

import urlparse,urllib2,urllib,re
import os
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[beeg.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos"            , title="Útimos videos"       , url="http://beeg.com/api/v5/index/main/0/pc"))
    itemlist.append( Item(channel=__channel__, action="listcategorias"    , title="Listado categorias"  , url="http://beeg.com/api/v5/index/main/0/pc"))
    itemlist.append( Item(channel=__channel__, action="search"            , title="Buscar"              , url="http://beeg.com/api/v5/index/search/0/pc?query=%s" ))
    return itemlist

def videos(item):
    logger.info("[beeg.py] videos")
    itemlist = []
    import json
    data = scrapertools.cache_page(item.url)  
    JSONData = json.loads(data)
    
    
    for Video in JSONData["videos"]:
      thumbnail = "http://img.beeg.com/236x177/" + Video["id"].encode("utf8") +  ".jpg"
      url = "https://api.beeg.com/api/v5/video/" + Video["id"].encode("utf8")
      title = Video["title"].encode("utf8")
      itemlist.append( Item(channel=__channel__, action="play" , title=title , url=url, thumbnail=thumbnail, plot="", show="", viewmode="movie", folder=True))
      
    #Paginador
    Actual = int(scrapertools.get_match(item.url,'http://beeg.com/api/v5/index/[^/]+/([0-9]+)/pc'))
    if JSONData["pages"]-1 > Actual:
      scrapedurl = item.url.replace("/"+str(Actual)+"/", "/"+str(Actual+1)+"/")
      itemlist.append( Item(channel=__channel__, action="videos", title="Página Siguiente" , url=scrapedurl , thumbnail="" , folder=True) )


    
    return itemlist

def listcategorias(item):
    logger.info("[beeg.py] listcategorias")
    itemlist = []
    import json
    data = scrapertools.cache_page(item.url)  
    JSONData = json.loads(data)
    
    
    for Tag in JSONData["tags"]["popular"]:
      url = "http://beeg.com/api/v5/index/tag/0/pc?tag=" + Tag.encode("utf8")
      title = Tag.encode("utf8")
      title = title[:1].upper() + title[1:]
      itemlist.append( Item(channel=__channel__, action="videos" , title=title , url=url, folder=True))

    return itemlist
  
def search(item,texto):
    logger.info("[beeg.py] search")

    texto = texto.replace(" ","+")
    item.url = item.url % (texto)
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def play(item):
    logger.info("[beeg.py] findvideos")
    itemlist = []
    import json
    data = scrapertools.cache_page(item.url)  
    JSONData = json.loads(data)
    for key in JSONData:
      videourl = re.compile("([0-9]+p)",re.DOTALL).findall(key)
      if videourl: 
        videourl= videourl[0]
        if not JSONData[videourl] == None:
          url = JSONData[videourl].encode("utf8")
          url = url.replace("{DATA_MARKERS}","data=pc.ES")
          if not url.startswith("http:"): url = "http:" + url
          title = videourl.encode("utf8")
          itemlist.append( Item(channel=__channel__, action="play" , fulltitle=title, title=item.title , url=url, thumbnail=item.thumbnail, server="directo", folder=False))
      
    itemlist.sort(key=lambda item: item.fulltitle.lower(), reverse=True)
    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    # mainlist
    mainlist_items = mainlist(Item())
    videos_items = videos(mainlist_items[0])
    play_items = play(videos_items[0])

    if len(play_items)==0:
        return False

    return True
