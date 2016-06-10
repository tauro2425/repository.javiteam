# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Inkapelis
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "inkapelis"
__category__ = "F,L,VOS"
__type__ = "generic"
__title__ = "Inkapelis"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.inkapelis mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades"      , action="lista"    , url="http://www.inkapelis.com/", extra = "Novedades"))
    itemlist.append( Item(channel=__channel__, title="Estrenos"       , action="lista"   , url="http://www.inkapelis.com/genero/estrenos/"))
    itemlist.append( Item(channel=__channel__, title="Géneros"  , action="generos"   , url="http://www.inkapelis.com/"))
    itemlist.append( Item(channel=__channel__, title="Buscar..."  , action="search"   , url="http://www.inkapelis.com/?s="))
    itemlist.append( Item(channel=__channel__, title="Búsqueda por actor"  , action="search"   , url="http://www.inkapelis.com/actor/"))
    return itemlist


def search(item,texto):
    logger.info("pelisalacarta.inkapelis search")
    itemlist = []
    item.extra = "Buscar"
    if item.title == "Búsqueda por actor": texto = texto.replace("+","-")
    item.url = item.url + texto
    try:
        itemlist = lista(item)
    except:
	    pass
    return itemlist


def generos(item):
    logger.info("pelisalacarta.channels.inkapelis generos")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    patron = '<li class="cat-item cat-item-.*?><a href="([^"]+)".*?>(.*?)<b>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle == "Eroticas +18 ":
            if config.get_setting("enableadultmode") == "false": continue
            itemlist.append( Item(channel=__channel__, action='eroticas', title=scrapedtitle , url=scrapedurl , thumbnail="" , folder=True) )
        elif (scrapedtitle != "Estrenos ") and (scrapedtitle!= "Próximos Estrenos "):
            if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
            itemlist.append( Item(channel=__channel__, action='lista', title=scrapedtitle , url=scrapedurl , thumbnail="" , folder=True) )

    return itemlist

def lista(item):
    logger.info("pelisalacarta.channels.inkapelis lista")
    urlitem = item.url
    extra = item.extra
    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
	
	#IF en caso de busqueda
    if item.extra == "Buscar":
        # Extrae las entradas
        patron ='<div class="col-xs-2">.*?<a href="([^"]+)" title="([^"]+)"> <img src="([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            thumbnail = scrapedthumbnail.replace("w185","original")
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+thumbnail+"]")
            try:
                plot, fanart = info(scrapedtitle, scrapedthumbnail)
                itemlist.append( Item(channel=__channel__, action='findvideos', title=scrapedtitle , url=scrapedurl , thumbnail=thumbnail , plot=str(plot), fanart=fanart, folder=True) )
            except:
                itemlist.append( Item(channel=__channel__, action='findvideos', title=scrapedtitle , url=scrapedurl , thumbnail=thumbnail , plot="",  folder=True) )
		
        # Extrae la marca de la siguiente página
        if len(itemlist) > 0:
            patron ='<span class="current">.*?<\/span><a href="([^"]+)".*? title="([^"]+)">'
            matches = re.compile(patron,re.DOTALL).findall(data)
            for scrapedurl, scrapedtitle in matches:
                url = scrapedurl 
                title = "Página " + scrapedtitle
                if DEBUG: logger.info("title=["+title+"], url=["+url+"]")
                itemlist.append( Item(channel=__channel__, action='lista', title= title , url=url , thumbnail="", extra = "Buscar", folder=True) )


    else:
        # Extrae las entradas y lista la mitad

        if item.extra == "Novedades":
            data2 = data.split("<h3>Últimas Películas Agregadas</h3>", 1)
            entradas = re.compile('<div class="col-mt-5 postsh">(.*?)</div></div></div>',re.DOTALL|re.M).findall(data2[1])
        else:
            entradas = re.compile('<div class="col-mt-5 postsh">(.*?)</div></div></div>',re.DOTALL|re.M).findall(data)
        
        patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">'
        patron += '.*?<div class="idiomes"><div class="(.*?)">.*?'
        patron += '<img.*?src="([^"]+)".*?<span class="under-title">(.*?)</span>'
        for match in entradas[0:(len(entradas)/2)]:
            matches = re.compile(patron,re.DOTALL).findall(match)
            for calidad, url, scrapedtitle, idioma, scrapedthumbnail, category in matches:
			    #Salto entradas adultos
                if category == "Eroticas +18": continue
                title = scrapedtitle + " -"+calidad+ " "
                if 'class="proximamente"' in match: title += "Próximamente " 
                title += idioma
                thumbnail = scrapedthumbnail.replace("w185","original")
                if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
                try:
                    plot, fanart = info(scrapedtitle, scrapedthumbnail)
                    itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail , plot=str(plot), fanart=fanart, folder=True) )
                except:
                    itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail , plot="", folder=True) )
	    
        itemlist.append( Item(channel=__channel__, action='lista2', title= "Siguiente" , url=urlitem, extra=extra, folder=True) )

    return itemlist

def lista2(item):
    logger.info("pelisalacarta.channels.inkapelis lista2")
    itemlist = []
    extra = item.extra
    data = scrapertools.cachePage(item.url)
    # Extrae la mitad restante
    if item.extra == "Novedades":
        data2 = data.split("<h3>Últimas Películas Agregadas</h3>", 1)
        entradas = re.compile('<div class="col-mt-5 postsh">(.*?)</div></div></div>',re.DOTALL|re.M).findall(data2[1])
    else:
        entradas = re.compile('<div class="col-mt-5 postsh">(.*?)</div></div></div>',re.DOTALL|re.M).findall(data)
       
    patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">'
    patron += '.*?<div class="idiomes"><div class="(.*?)">.*?'
    patron += '<img.*?src="([^"]+)".*?<span class="under-title">(.*?)</span>'
    for match in entradas[(len(entradas)/2):]:
        matches = re.compile(patron,re.DOTALL).findall(match)
        for calidad, url, scrapedtitle, idioma, scrapedthumbnail, category in matches:
			#Salto entradas adultos
            if category == "Eroticas +18": continue
            title = scrapedtitle + " -"+calidad+ " "
            if 'class="proximamente"' in match: title += "Próximamente " 
            title += idioma
            thumbnail = scrapedthumbnail.replace("w185","original")
            if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
            try:
                plot, fanart = info(scrapedtitle, scrapedthumbnail)
                itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail , plot=str(plot), fanart=fanart, folder=True) )
            except:
                itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail , plot="", folder=True) )
	    

    # Extrae la marca de la siguiente página
    patron ='<span class="current">.*?<\/span><a href="http://www.inkapelis.com/page/(\d+)/'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedpage in matches:
        url = "http://www.inkapelis.com/page/"+scrapedpage
        if DEBUG: logger.info("url=["+url+"]")
        itemlist.append( Item(channel=__channel__, action='lista', title= "Siguiente" , url=url , extra=extra, folder=True) )

    return itemlist

def eroticas(item):
    logger.info("pelisalacarta.channels.inkapelis eroticas")
    urlitem = item.url
    extra = item.extra
    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
	
    # Extrae las entradas y lista la mitad
    entradas = re.compile('<div class="col-mt-5 postsh">(.*?)</div></div></div>',re.DOTALL|re.M).findall(data)
    patron = '<div class="poster-media-card([^"]+)">.*?<a href="([^"]+)" title="([^"]+)">'
    patron += '.*?<div class="idiomes"><div class="(.*?)">.*?'
    patron += '<img.*?src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for calidad, url, scrapedtitle, idioma, scrapedthumbnail in matches:
        title = scrapedtitle + " -"+calidad+ " " + idioma
        thumbnail = scrapedthumbnail.replace("w185","original")
        if DEBUG: logger.info("title=["+title+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action='findvideos_ero', title=title , url=url , thumbnail=thumbnail, folder=True) )

    # Extrae la marca de la siguiente página
    patron ='<span class="current">.*?<\/span><a href="http://www.inkapelis.com/page/(\d+)/'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedpage in matches:
        url = "http://www.inkapelis.com/page/"+scrapedpage
        if DEBUG: logger.info("url=["+url+"]")
        itemlist.append( Item(channel=__channel__, action='lista', title= "Siguiente" , url=url , extra=extra, folder=True) )
	    
    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.inkapelis findvideos")
    
    itemlist = []
    # Descarga la pagina
    data = scrapertools.cachePage(item.url)
	#Saca la sinopsis, el trailer y el fanart y los incluye si no los tenía
    sinopsis = scrapertools.find_single_match(data, '<h2>Sinopsis</h2>.*?>(.*?)</p>')
    sinopsis = scrapertools.htmlclean(sinopsis)
    key = scrapertools.find_single_match(data, 'id="trailerpro">.*?src="//www.youtube.com/embed/(.*?)"')
    trailer = None
    if key != "": trailer = "plugin://plugin.video.youtube/?action=play_video&videoid="+key
    if item.plot.find("'plot': ''"):
        item.plot = item.plot.replace("'plot': ''", "'plot': '"+sinopsis+"'")
    if item.plot == "":
        item.plot = "{'infoLabels': {'plot': "+sinopsis+"}}"
    if trailer: item.plot = item.plot.replace("}}",",'trailer': '"+trailer+"'}}")
    fanart = scrapertools.find_single_match(data, '<div class="episode-selector-element">.*?src="([^"]+)"')
    if not item.fanart.startswith("http://image.tmdb.org"): item.fanart = fanart

    #Busca los enlaces
    patronlinks = '<td><a href="([^"]+)".*?title="([^"]+)".*?<td>([^"]+)<\/td><td>([^"]+)<\/td>'
    matches = re.compile(patronlinks,re.DOTALL).findall(data)
    
    for url, server, idioma, calidad in matches:
        servidor = server
        if servidor == "Embed" : servidor = "Nowvideo"
        title = servidor + " - " + idioma + " - " + calidad
        itemlist.append( Item(channel=__channel__, action="play", title= title  , url=url , thumbnail=item.thumbnail, fanart=item.fanart, plot= item.plot, folder=True) )

    patronembed = 'id="(embed[0-9])".*?<div class="calishow">(.*?)<(.*?)<div class="clear">'
    matches = re.compile(patronembed,re.DOTALL).findall(data)
    for title, calidad, url in matches:
        title = scrapertools.find_single_match(url,"(?:http://|https://|//)(.*?)(?:embed.|videoembed|)/")
        title = title.capitalize() + " - "+calidad
        itemlist.append( Item(channel=__channel__, action="play", title= title  , url=url , thumbnail=item.thumbnail, fanart=item.fanart, plot= item.plot, folder=True) )

    return itemlist

def findvideos_ero(item):
    logger.info("pelisalacarta.inkapelis findvideos_ero")
    
    itemlist = []
    # Descarga la pagina
    data = scrapertools.cachePage(item.url)
    #Busca los enlaces
    patronlinks = '<td><a href="([^"]+)".*?title="([^"]+)".*?<td>([^"]+)<\/td><td>([^"]+)<\/td>'
    matches = re.compile(patronlinks,re.DOTALL).findall(data)
    
    for url, server, idioma, calidad in matches:
        servidor = server
        if servidor == "Embed" : servidor = "Nowvideo"
        title = servidor + " - " + idioma + " - " + calidad
        itemlist.append( Item(channel=__channel__, action="play", title= title  , url=url , thumbnail=item.thumbnail, fanart=item.fanart, plot= item.plot, folder=True) )

    patronembed = 'id="(embed[0-9])".*?<div class="calishow">(.*?)<(.*?)<div class="clear">'
    matches = re.compile(patronembed,re.DOTALL).findall(data)
    for title, calidad, url in matches:
        title = scrapertools.find_single_match(url,"(?:http://|https://|//)(.*?)(?:embed.|videoembed|)/")
        title = title.capitalize() + " - "+calidad
        itemlist.append( Item(channel=__channel__, action="play", title= title  , url=url , thumbnail=item.thumbnail, fanart=item.fanart, plot= item.plot, folder=True) )

    return itemlist
	
def play(item):
    logger.info("pelisalacarta.inkapelis play")
    itemlist = servertools.find_video_items(data=item.url)
    return itemlist

def info(title, thumbnail):
    logger.info("pelisalacarta.inkapelis info")
    infoLabels={}
    plot={}
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "movie")
        count = 0
        if oTmdb.total_results > 0:
            #Mientras el thumbnail no coincida con el del resultado de la búsqueda, pasa al siguiente resultado
            while oTmdb.get_poster(size="w185") != thumbnail:
                count += 1
                oTmdb.load_resultado(index_resultado=count)
                if count == oTmdb.total_results : break
            infoLabels['code'] = oTmdb.get_id()
            infoLabels['plot'] = oTmdb.get_sinopsis()
            infoLabels['title'] = oTmdb.result["title"]
            infoLabels['year']= oTmdb.result["release_date"][:4]
            infoLabels['genre'] = ", ".join(oTmdb.result["genres"])
            infoLabels['rating'] = float(oTmdb.result["vote_average"])
            fanart=oTmdb.get_backdrop()
            plot['infoLabels']=infoLabels
            return plot, fanart
    except:
        pass	