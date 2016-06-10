# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para jkanime
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

DEBUG = config.get_setting("debug")

__category__ = "A"
__type__ = "generic"
__title__ = "JKanime"
__channel__ = "jkanime"
__language__ = "ES"
__creationdate__ = "20121015"

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.jkanime mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="ultimos" , title="Últimos"           , url="http://jkanime.net/" ))
    itemlist.append( Item(channel=__channel__, action="letras"  , title="Listado Alfabetico", url="http://jkanime.net/" ))
    itemlist.append( Item(channel=__channel__, action="generos" , title="Listado por Genero", url="http://jkanime.net/" ))
    itemlist.append( Item(channel=__channel__, action="search"  , title="Buscar" ))
  
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.jkanime search")
    if item.url=="":
        item.url="http://jkanime.net/buscar/%s/"
    texto = texto.replace(" ","+")
    item.url = item.url % texto
    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def ultimos(item):
    logger.info("pelisalacarta.channels.jkanime ultimos")
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<ul class="latestul">(.*?)</ul>')
    
    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)    

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot=plot))        

    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.jkanime generos")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<div class="genres">(.*?)</div>')
    
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)    

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="series" , title=title , url=url, thumbnail=thumbnail, plot=plot))        

    return itemlist

def letras(item):
    logger.info("pelisalacarta.channels.jkanime letras")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<ul class="animelet">(.*?)</ul>')
    
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)    

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="series" , title=title , url=url, thumbnail=thumbnail, plot=plot))        

    return itemlist

def series(item):
    logger.info("pelisalacarta.channels.jkanime series")

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas
    '''
    <table class="search">
    <tr>
    <td rowspan="2">
    <a href="http://jkanime.net/basilisk-kouga-ninpou-chou/"><img src="http://jkanime.net/assets/images/animes/thumbnail/basilisk-kouga-ninpou-chou.jpg" width="50" /></a>
    </td>
    <td><a class="titl" href="http://jkanime.net/basilisk-kouga-ninpou-chou/">Basilisk: Kouga Ninpou Chou</a></td>
    <td rowspan="2" style="width:50px; text-align:center;">Serie</td>
    <td rowspan="2" style="width:50px; text-align:center;" >24 Eps</td>
    </tr>
    <tr>
    <td><p>Basilisk, considerada una de las mejores series del genero ninja, nos narra la historia de dos clanes ninja separados por el odio entre dos familias. Los actuales representantes, Kouga Danjo del clan Kouga y Ogen del clan&#8230; <a class="next" href="http://jkanime.net/basilisk-kouga-ninpou-chou/">seguir leyendo</a></p></td>
    </tr>
    </table>
    '''
    patron  = '<table class="search[^<]+'
    patron += '<tr[^<]+'
    patron += '<td[^<]+'
    patron += '<a href="([^"]+)"><img src="([^"]+)"[^<]+</a>[^<]+'
    patron += '</td>[^<]+'
    patron += '<td><a[^>]+>([^<]+)</a></td>[^<]+'
    patron += '<td[^>]+>([^<]+)</td>[^<]+'
    patron += '<td[^>]+>([^<]+)</td>[^<]+'
    patron += '</tr>[^<]+'
    patron += '<tr>[^<]+'
    patron += '<td>(.*?)</td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    itemlist = []
    
    for scrapedurl, scrapedthumbnail,scrapedtitle,line1,line2,scrapedplot in matches:
        title = scrapedtitle.strip()+" ("+line1.strip()+") ("+line2.strip()+")"
        extra = line2.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        thumbnail = thumbnail.replace("thumbnail","image")
        plot = scrapertools.htmlclean(scrapedplot)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="episodios" , title=title , url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, extra=extra, viewmode="movie_with_plot"))        

    try:
        siguiente = scrapertools.get_match(data,'<a class="listsiguiente" href="([^"]+)" >Resultados Siguientes')
        scrapedurl = urlparse.urljoin(item.url,siguiente)
        scrapedtitle = ">> Pagina Siguiente"
        scrapedthumbnail = ""
        scrapedplot = ""

        itemlist.append( Item(channel=__channel__, action="series", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )
    except:
        pass
    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.jkanime episodios")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    
    scrapedplot = scrapertools.get_match(data,'<meta name="description" content="([^"]+)"/>')
    scrapedthumbnail = scrapertools.find_single_match(data, '<div class="separedescrip">.*?src="([^"]+)"')

    
    idserie = scrapertools.get_match(data,"ajax/pagination_episodes/(\d+)/")
    logger.info("idserie="+idserie)
    if " Eps" in item.extra:
        caps_x = item.extra
        caps_x = caps_x.replace(" Eps","")
        capitulos = int(caps_x)
        paginas = capitulos/10
        if capitulos%10>0:
            paginas += 1
    else:
        paginas = 1
    
    logger.info("idserie="+idserie)
    for numero in range(1,paginas + 1):

        numero_pagina = str(numero)
        headers = []
        headers.append( [ "User-Agent" , "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:16.0) Gecko/20100101 Firefox/16.0" ] )
        headers.append( [ "Referer" , item.url ] )
        data2 = scrapertools.cache_page("http://jkanime.net/ajax/pagination_episodes/"+idserie+"/"+numero_pagina+"/")
        logger.info("data2="+data2)
    
        '''
        [{"number":"1","title":"Rose of Versailles - 1"},{"number":"2","title":"Rose of Versailles - 2"},{"number":"3","title":"Rose of Versailles - 3"},{"number":"4","title":"Rose of Versailles - 4"},{"number":"5","title":"Rose of Versailles - 5"},{"number":"6","title":"Rose of Versailles - 6"},{"number":"7","title":"Rose of Versailles - 7"},{"number":"8","title":"Rose of Versailles - 8"},{"number":"9","title":"Rose of Versailles - 9"},{"number":"10","title":"Rose of Versailles - 10"}]
        [{"id":"14199","title":"GetBackers - 1","number":"1","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14200","title":"GetBackers - 2","number":"2","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14201","title":"GetBackers - 3","number":"3","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14202","title":"GetBackers - 4","number":"4","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14203","title":"GetBackers - 5","number":"5","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14204","title":"GetBackers - 6","number":"6","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14205","title":"GetBackers - 7","number":"7","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14206","title":"GetBackers - 8","number":"8","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14207","title":"GetBackers - 9","number":"9","animes_id":"122","timestamp":"2012-01-04 16:59:30"},{"id":"14208","title":"GetBackers - 10","number":"10","animes_id":"122","timestamp":"2012-01-04 16:59:30"}]
        '''
        patron = '"number"\:"(\d+)","title"\:"([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data2)
    
        #http://jkanime.net/get-backers/1/
        for numero,scrapedtitle in matches:
            title = scrapedtitle.strip()
            url = urlparse.urljoin(item.url,numero)
            thumbnail = scrapedthumbnail
            plot = scrapedplot
            if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

            itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot))        

    if len(itemlist)==0:
        try:
            porestrenar = scrapertools.get_match(data,'<div[^<]+<span class="labl">Estad[^<]+</span[^<]+<span[^>]+>Por estrenar</span>')
            itemlist.append( Item(channel=__channel__, action="findvideos" , title="Serie por estrenar" , url="", thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot, server="directo", folder=False))
        except:
            pass

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.jkanime episodios")

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    logger.info("pelisalacarta.channels.jkanime data="+data)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.channel=__channel__
        videoitem.folder=False

    #180upload: sp1.e=hh7pmxk553kj
    code = scrapertools.find_single_match(data,"sp1.e=([a-z0-9]+)")
    if code!="":
        mediaurl = "http://180upload.com/"+code
        itemlist.append( Item(channel=__channel__, action="play" , title="Ver en 180upload" , url=mediaurl, thumbnail=item.thumbnail, fanart=item.thumbnail, plot=item.plot, server="one80upload", folder=False))
    
    #upafile: spu.e=idyoybh552bf
    code = scrapertools.find_single_match(data,"spu.e=([a-z0-9]+)")
    if code!="":
        mediaurl = "http://upafile.com/"+code
        itemlist.append( Item(channel=__channel__, action="play" , title="Ver en upafile" , url=mediaurl, thumbnail=item.thumbnail, fanart=item.thumbnail, plot=item.plot, server="upafile", folder=False))

    mediaurl = scrapertools.find_single_match(data,'flashvars\="file\=([^\&]+)\&')
    if mediaurl!="":
        itemlist.append( Item(channel=__channel__, action="play" , title="Ver en jkanime" , url=mediaurl, thumbnail=item.thumbnail, fanart=item.thumbnail, plot=item.plot, server="directo", folder=False, extra=item.url))
    
    mediaurl = scrapertools.find_single_match(data,"url\: '(https://jkanime.net/stream/jkget/[^']+)'")
    if mediaurl!="":
        itemlist.append( Item(channel=__channel__, action="play" , title="Enlace encontrado en jkanime" , url=mediaurl, thumbnail=item.thumbnail, fanart=item.thumbnail, plot=item.plot, server="directo", folder=False, extra=item.url))

    patron = 'src=(https:\/\/jkanime.net\/jk.php\?u=stream\/jkmedia\/[^"]+) '
    matches = re.compile(patron,re.DOTALL).findall(data)
    for mediaurl in matches:
        if mediaurl!="":
            mediaurl = mediaurl.replace("jk.php?u=stream", "stream")
            itemlist.append( Item(channel=__channel__, action="play" , title="Enlace encontrado en jkanime" , url=mediaurl, thumbnail=item.thumbnail, fanart=item.thumbnail, plot=item.plot, server="directo", folder=False, extra=item.url))

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
    series_items = ultimos(mainlist_items[0])
    
    for serie_item in series_items:
        episodios_items = episodios(serie_item)

        bien = False
        for episodio_item in episodios_items:
            mirrors = findvideos(item=episodio_item)
            if len(mirrors)>0:
                bien = True
                break
        
    return bien