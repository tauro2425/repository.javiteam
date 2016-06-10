# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para novedades
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "novedades"
__category__ = "F"
__type__ = "generic"
__title__ = "Novedades"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item,preferred_thumbnail="squares"):
    logger.info("pelisalacarta.channels.novedades mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="peliculas"            , title="Películas", thumbnail="http://media.tvalacarta.info/pelisalacarta/"+preferred_thumbnail+"/thumb_canales_peliculas.png",viewmode="movie"))
    itemlist.append( Item(channel=__channel__, action="peliculas_infantiles" , title="Para niños", thumbnail="http://media.tvalacarta.info/pelisalacarta/"+preferred_thumbnail+"/thumb_canales_infantiles.png",viewmode="movie"))
    itemlist.append( Item(channel=__channel__, action="series"               , title="Episodios de series", thumbnail="http://media.tvalacarta.info/pelisalacarta/"+preferred_thumbnail+"/thumb_canales_series.png",viewmode="movie"))
    itemlist.append( Item(channel=__channel__, action="anime"                , title="Episodios de anime", thumbnail="http://media.tvalacarta.info/pelisalacarta/"+preferred_thumbnail+"/thumb_canales_anime.png",viewmode="movie"))
    itemlist.append( Item(channel=__channel__, action="documentales"         , title="Documentales", thumbnail="http://media.tvalacarta.info/pelisalacarta/"+preferred_thumbnail+"/thumb_canales_documentales.png",viewmode="movie"))

    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.channels.novedades peliculas")

    itemlist = []

    import zpeliculas
    item.url = "http://www.zpeliculas.com"
    itemlist.extend( zpeliculas.peliculas(item) )

    import cinetux
    item.url = "http://www.cinetux.org/"
    itemlist.extend( cinetux.peliculas(item) )

    import divxatope
    item.url = "http://www.divxatope.com/categoria/peliculas-castellano"
    itemlist.extend( divxatope.lista(item) )

    import yaske
    item.url = "http://www.yaske.cc/"
    itemlist.extend( yaske.peliculas(item) )

    sorted_itemlist = []

    for item in itemlist:

        if item.extra!="next_page" and not item.title.startswith(">>"):
            item.title = item.title + " ["+item.channel+"]"
            sorted_itemlist.append(item)

    sorted_itemlist = sorted(sorted_itemlist, key=lambda Item: Item.title)    

    return sorted_itemlist

def peliculas_infantiles(item):
    logger.info("pelisalacarta.channels.novedades peliculas_infantiles")

    itemlist = []

    import zpeliculas
    item.url = "http://www.zpeliculas.com/peliculas/p-animacion/"
    itemlist.extend( zpeliculas.peliculas(item) )

    import cinetux
    item.url = "http://www.cinetux.org/genero/infantil"
    itemlist.extend( cinetux.peliculas(item) )

    import yaske
    item.url = "http://www.yaske.cc/es/peliculas/custom/?gender=animation"
    itemlist.extend( yaske.peliculas(item) )

    import oranline
    item.url = "http://www.oranline.com/Películas/infantil/"
    itemlist.extend( oranline.peliculas(item) )

    sorted_itemlist = []

    for item in itemlist:

        if item.extra!="next_page" and not item.title.startswith(">>"):
            item.title = item.title + " ["+item.channel+"]"
            sorted_itemlist.append(item)

    sorted_itemlist = sorted(sorted_itemlist, key=lambda Item: Item.title)    

    return sorted_itemlist

def series(item):
    logger.info("pelisalacarta.channels.novedades series")

    itemlist = []

    import divxatope
    item.url = "http://www.divxatope.com/categoria/series"
    itemlist.extend( divxatope.lista(item) )

    import seriesflv
    item.url = "es"
    itemlist.extend( seriesflv.ultimos_episodios(item) )

    sorted_itemlist = []

    for item in itemlist:

        if item.extra!="next_page" and not item.title.startswith(">>"):
            item.title = item.title + " ["+item.channel+"]"
            sorted_itemlist.append(item)

    sorted_itemlist = sorted(sorted_itemlist, key=lambda Item: Item.title)    

    return sorted_itemlist

def anime(item):
    logger.info("pelisalacarta.channels.novedades anime")

    itemlist = []

    import animeid
    item.url = "http://animeid.tv/"
    itemlist.extend( animeid.novedades_episodios(item) )

    import animeflv
    item.url = "http://animeflv.net/"
    itemlist.extend( animeflv.novedades(item) )

    sorted_itemlist = []

    for item in itemlist:

        if item.extra!="next_page" and not item.title.startswith(">>"):
            item.title = item.title + " ["+item.channel+"]"
            sorted_itemlist.append(item)

    sorted_itemlist = sorted(sorted_itemlist, key=lambda Item: Item.title)    

    return sorted_itemlist

def documentales(item):
    logger.info("pelisalacarta.channels.novedades documentales")

    itemlist = []

    import documaniatv
    item.url = "http://www.documaniatv.com/newvideos.html"
    itemlist.extend( documaniatv.novedades(item) )

    import oranline
    item.url = "http://oranline.com/Pel%C3%ADculas/documentales/"
    itemlist.extend( oranline.peliculas(item) )

    sorted_itemlist = []

    for item in itemlist:

        if item.extra!="next_page" and not item.title.startswith(">>"):
            item.title = item.title + " ["+item.channel+"]"
            sorted_itemlist.append(item)

    sorted_itemlist = sorted(sorted_itemlist, key=lambda Item: Item.title)    

    return sorted_itemlist
