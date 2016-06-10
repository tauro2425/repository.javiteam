# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para hentaiflv (por Kira)
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from servers import servertools

DEBUG = config.get_setting("debug")

__category__ = "A,X"
__type__ = "generic"
__title__ = "Hentaiflv"
__channel__ = "hentaiflv"
__language__ = "ES"
__creationdate__ = "20140414"

HENTAIFLV_REQUEST_HEADERS = []
HENTAIFLV_REQUEST_HEADERS.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0"])
HENTAIFLV_REQUEST_HEADERS.append(["Accept-Encoding","gzip, deflate"])
HENTAIFLV_REQUEST_HEADERS.append(["Connection","keep-alive"])
HENTAIFLV_REQUEST_HEADERS.append(["Accept","application/json, text/plain, */*"])
HENTAIFLV_REQUEST_HEADERS.append(["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
HENTAIFLV_REQUEST_HEADERS.append(["Content-Type","application/x-www-form-urlencoded; charset=UTF-8"])

def isGeneric():
    return True

def get_page(url,post):
    logger.info("pelisalacarta.channels.hentaiflv get_page")

    headers = HENTAIFLV_REQUEST_HEADERS[:]
    headers.append(["Referer",url])
    headers.append(["Content-Length",len(post)])
    data = scrapertools.cache_page("http://hentaiflv.net/api/",post,headers=headers)

    return data

def mainlist(item):
    logger.info("pelisalacarta.channels.hentaiflv mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="novedades"     , title="Recientes"           , url="http://hentaiflv.net/hentais/recientes/", extra="acc=hentais_search&type=recent&value=&page=1" ))
    itemlist.append( Item(channel=__channel__, action="novedades"     , title="Sin censura"         , url="http://hentaiflv.net/hentais/sin-censura/", extra="acc=hentais_search&type=nocensure&value=&page=1" ))
    itemlist.append( Item(channel=__channel__, action="search"        , title="Buscar"              , url="http://hentaiflv.net/hentais/buscar/###/", extra="acc=hentais_search&type=search&value=###&page=1" ))
  
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.hentaiflv search")

    if item.url=="":
        item.url = "http://hentaiflv.net/hentais/buscar/###/"

    if item.extra=="":
        item.extra = "acc=hentais_search&type=search&value=###&page=1"

    texto = texto.replace(" ","+")
    item.url = item.url.replace("###",texto)
    item.extra = item.extra.replace("###",texto)
    
    try:
        return novedades(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def novedades(item):
    logger.info("pelisalacarta.channels.hentaiflv novedades")

    # Descarga la pagina
    data = get_page(item.url,item.extra)
    logger.info("data="+data)

    # Carga el json
    json_data = jsontools.load_json(data)

    # Para cada entrada...
    itemlist = []
    for entry in json_data["data"]:
        title = entry["Nombre"]
        url = entry["Url"]
        thumbnail = entry["imagen"]
        plot = "Censurado: "+entry["Censurado"]+"\n"+entry["Sinopsis"]
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, viewmode="movie_with_plot"))

    next_page = json_data["page"]["current"]
    itemlist.append( Item(channel=__channel__, action="novedades" , title=">> Página siguiente" , url=item.url, extra="acc=hentais_search&type=recent&value=&page="+str( int(next_page)+1 )))

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.hentaiflv episodios")

    # Descarga la pagina
    url = urlparse.urljoin("http://hentaiflv.net/hentai/",item.url)+".html"
    post = "acc=hentai&slug="+item.url

    data = get_page(url,post)
    logger.info("data="+data)

    # Carga el json
    json_data = jsontools.load_json(data)

    # Para cada entrada...
    itemlist = []
    for entry in json_data["episodes"]:
        title = "Episodio "+entry["episodio"]
        url = "http://hentaiflv.net/api/player.php?slug="+item.url+"&episode="+entry["episodio"]
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, viewmode="movie_with_plot"))

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True

    # mainlist
    mainlist_items = mainlist(Item())
    
    # Comprueba que todas las opciones tengan algo (excepto el buscador)
    for mainlist_item in mainlist_items:
        if mainlist_item.action!="search":
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
            if len(itemlist)==0:
                return false

    # Comprueba si alguno de los vídeos de "Novedades" devuelve mirrors
    episodios_items = novedades(mainlist_items[0])

    bien = False
    for episodio_item in episodios_items:
        mirrors = findvideos(episodio_item)
        if len(mirrors)>0:
            bien = True
            break

    return bien
