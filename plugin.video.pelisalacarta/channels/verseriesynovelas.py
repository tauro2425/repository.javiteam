# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para verseriesynovelas
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re, urllib2, time
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "verseriesynovelas"
__category__ = "S,VOS,L"
__type__ = "generic"
__title__ = "Ver Series y Novelas"
__language__ = "ES"

DEBUG = config.get_setting("debug")

host = "http://www.verseriesynovelas.tv"

headers = [
    ["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"],
    ["Accept-Encoding","gzip, deflate"],
    ["Referer",host]
    ]

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.verseriesynovelas mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Series [Nuevos Capítulos]"         , action="novedades", url="http://www.verseriesynovelas.tv/archivos/nuevo", thumbnail= "http://i.imgur.com/ZhQknRE.png", fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append( Item(channel=__channel__, title="Series [Últimas Series]"   , action="ultimas", url="http://www.verseriesynovelas.tv/", thumbnail= "http://i.imgur.com/ZhQknRE.png", fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append( Item(channel=__channel__, title="Series [Lista de Series A-Z]"       , action="indices", url="http://www.verseriesynovelas.tv/", thumbnail= "http://i.imgur.com/ZhQknRE.png", fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append( Item(channel=__channel__, title="Series [Categorías]"   , action="indices", url="http://www.verseriesynovelas.tv/", thumbnail= "http://i.imgur.com/ZhQknRE.png", fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append( Item(channel=__channel__, title="Buscar..."      , action="search", thumbnail= "http://i.imgur.com/ZhQknRE.png", fanart="http://i.imgur.com/9loVksV.png"))
    return itemlist

def indices(item):
    logger.info("pelisalacarta.channels.verseriesynovelas indices")

    itemlist = []
    data = anti_cloudflare(item.url)
    data = data.replace("\n","").replace("\t","")

    if item.title == "Series [Categorías]":
        bloque = scrapertools.find_single_match(data, '<span>Seleccion tu categoria</span>(.*?)</section>')
        matches = scrapertools.find_multiple_matches(bloque, '<li.*?<a href="([^"]+)">(.*?)</a>')
        for url, title in matches:
            itemlist.append(Item( channel=__channel__, action="ultimas", title=title, url=url, fanart=item.fanart ) )
    else:
        bloque = scrapertools.find_single_match(data, '<ul class="alfabetico">(.*?)</ul>')
        matches = scrapertools.find_multiple_matches(bloque, '<li.*?<a href="([^"]+)".*?>(.*?)</a>')
        for url, title in matches:
            itemlist.append(Item( channel=__channel__, action="ultimas", title=title, url=url, fanart=item.fanart ) )

    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.verseriesynovelas search")
    item.url = "http://www.verseriesynovelas.tv/archivos/h1/?s=" + texto
    if item.title == "Buscar...": return ultimas(item)
    else:
        try:
            return busqueda(item)
        except:
            import sys
            for line in sys.exc_info():
                logger.error( "%s" % line )
            return []

def busqueda(item):
    logger.info("pelisalacarta.channels.verseriesynovelas busqueda")
    itemlist = []
    data = anti_cloudflare(item.url)
    data = data.replace("\n","").replace("\t","")

    bloque = scrapertools.find_single_match(data, '<ul class="list-paginacion">(.*?)</section>')
    patron = '<li><a href=(.*?)</li>'
    bloque2 = scrapertools.find_multiple_matches(bloque, patron)
    for match in bloque2:
        patron = '([^"]+)".*?<img class="fade" src="([^"]+)".*?<h2>(.*?)</h2>'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace(" online","")
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append( Item(channel=__channel__, action='episodios', title= scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, fanart=item.fanart, fulltitle=scrapedtitle, folder=True) )
    #Paginación
    patron = '<a class="nextpostslink".*?href="([^"]+)">'
    match = scrapertools.find_single_match(data, patron)
    if len(match) > 0:
        itemlist.append( Item(channel=__channel__, action='busqueda', title= ">>Siguiente Página" , url=match , fanart=item.fanart, folder=True) )

    return itemlist


def novedades(item):
    logger.info("pelisalacarta.channels.verseriesynovelas novedades")
    itemlist = []
    data = anti_cloudflare(item.url)
    data = data.replace("\n","").replace("\t","")

    bloque = scrapertools.find_single_match(data, '<section class="list-galeria">(.*?)</section>')
    patron = '<li><a href=(.*?)</a></li>'
    bloque2 = scrapertools.find_multiple_matches(bloque, patron)
    for match in bloque2:
        patron = '([^"]+)".*?<img class="fade" src="([^"]+)".*?title="(?:ver |)([^"]+)"'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
            titleinfo = scrapertools.decodeHtmlentities(scrapedtitle)
            titleinfo = re.split("Temporada", titleinfo, flags=re.IGNORECASE)[0]
            try:
                sinopsis, fanart, thumbnail = info(titleinfo)
                if thumbnail == "": thumbnail = scrapedthumbnail
            except:
                sinopsis = ""
                fanart = item.fanart
                thumbnail = scrapedthumbnail
                pass
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)+ " "
            if "ES.png" in match: scrapedtitle += "[COLOR sandybrown][CAST][/COLOR]"
            if "SUB.png" in match: scrapedtitle += "[COLOR green][VOSE][/COLOR]"
            if "LA.png" in match: scrapedtitle += "[COLOR red][LAT][/COLOR]"
            if "EN.png" in match: scrapedtitle += "[COLOR blue][V.O][/COLOR]"
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append( Item(channel=__channel__, action='findvideos', title= scrapedtitle , url=scrapedurl , thumbnail=thumbnail, fanart=fanart, fulltitle=scrapedtitle, plot=str(sinopsis), folder=True) )
    #Paginación
    patron = '<a class="nextpostslink".*?href="([^"]+)">'
    match = scrapertools.find_single_match(data, patron)
    if len(match) > 0:
        itemlist.append( Item(channel=__channel__, action='novedades', title= ">>Siguiente Página" , url=match , fanart=item.fanart, folder=True) )

    return itemlist

def ultimas(item):
    logger.info("pelisalacarta.channels.verseriesynovelas ultimas")
    itemlist = []
    data = anti_cloudflare(item.url)
    data = data.replace("\n","").replace("\t","")

    bloque = scrapertools.find_single_match(data, '<ul class="list-paginacion">(.*?)</section>')
    patron = '<li><a href=(.*?)</li>'
    bloque2 = scrapertools.find_multiple_matches(bloque, patron)
    for match in bloque2:
        patron = '([^"]+)".*?<img class="fade" src="([^"]+)".*?<h2>(.*?)</h2>'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace(" online","")
            titleinfo = re.sub(r'(?i)((primera|segunda|tercera|cuarta|quinta|sexta) [Tt]emporada)', "Temporada", scrapedtitle)
            titleinfo = titleinfo.split('Temporada')[0].strip()
            try:
                sinopsis, fanart, thumbnail = info(titleinfo)
                if thumbnail == "": thumbnail = scrapedthumbnail
            except:
                sinopsis = ""
                fanart = item.fanart
                thumbnail = scrapedthumbnail
                pass
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+thumbnail+"]")
            itemlist.append( Item(channel=__channel__, action='episodios', title= scrapedtitle , url=scrapedurl , thumbnail=thumbnail, fanart=fanart, fulltitle=titleinfo, plot=str(sinopsis), contentTitle=titleinfo, context="2", folder=True) )
    #Paginación
    patron = '<a class="nextpostslink".*?href="([^"]+)">'
    match = scrapertools.find_single_match(data, patron)
    if len(match) > 0:
        itemlist.append( Item(channel=__channel__, action='ultimas', title= ">>Siguiente Página" , url=match , fanart=item.fanart, folder=True) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.verseriesynovelas episodios")
    itemlist = []

    data = anti_cloudflare(item.url)
    data = data.replace("\n","").replace("\t","")
    if item.show == "":
        try:
            from core.tmdb import Tmdb
            otmdb= Tmdb(texto_buscado=item.fulltitle, tipo="tv")
        except:
            pass
    plot = scrapertools.find_single_match(data, '<p><p>(.*?)</p>')
    if len(plot)>0: plot = scrapertools.htmlclean(plot)
    patron = '<td data-th="Temporada"(.*?)</div>'
    bloque = scrapertools.find_multiple_matches(data, patron)
    for match in bloque:
        patron = '.*?href="([^"]+)".*?title="([^"]+)"'
        matches = scrapertools.find_multiple_matches(match, patron)
        for scrapedurl, scrapedtitle in matches:
            if item.show == "":
                try:
                    sinopsis, fanart, thumbnail = infoepi(otmdb, scrapedtitle.rsplit(' ', 1)[1], plot)
                    if thumbnail == "": thumbnail = item.thumbnail
                except:
                    thumbnail = item.thumbnail
                    fanart = item.fanart
                    sinopsis = plot
                    pass
            else:
                thumbnail = item.thumbnail
                fanart = item.fanart
                sinopsis = plot                
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)+ " "
            scrapedtitle = scrapedtitle.replace('Temporada','')
            if "ES.png" in match: scrapedtitle += "[COLOR sandybrown][CAST][/COLOR]"
            if "SUB.png" in match: scrapedtitle += "[COLOR green][VOSE][/COLOR]"
            if "LA.png" in match: scrapedtitle += "[COLOR red][LAT][/COLOR]"
            if "EN.png" in match: scrapedtitle += "[COLOR blue][V.O][/COLOR]"
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
            if item.show != "":
                scrapedtitle = scrapedurl + "%" + scrapedtitle
                scrapedurl = item.url
            itemlist.append( Item(channel=__channel__, action='findvideos', title= scrapedtitle , url=scrapedurl , thumbnail=thumbnail, fanart=fanart, fulltitle=item.fulltitle, plot=str(sinopsis), show=item.show, folder=True) )

    if len(itemlist) > 0 and item.show == "":
        if config.get_library_support():
            itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir esta temporada a la biblioteca[/COLOR]", url=item.url, action="add_serie_to_library", extra="episodios", fulltitle=item.fulltitle, show=item.fulltitle ))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.channels.verseriesynovelas findvideos")
    itemlist = []
    if item.title.startswith("http"): item.url = item.title.split('%')[0]
    data = anti_cloudflare(item.url)
    data = data.replace("\n","").replace("\t","")

    patron = '<tr><td data-th="Idioma">(.*?)</div>'
    bloque = scrapertools.find_multiple_matches(data, patron)
    for match in bloque:
        patron = '.*?data-th="Calidad">(.*?)<.*?'
        patron += '"Servidor".*?src="http://www.google.com/s2/favicons\?domain=(.*?)\.'
        patron += '.*?<td data-th="Enlace"><a href="(http://www.verseriesynovelas.tv/enlaces.php.*?)"'
        matches = scrapertools.find_multiple_matches(match, patron)
        for quality, server, url in matches:
            if server == "streamin": server = "streaminto"
            if server== "waaw": server = "netutv"
            if server == "ul": server = "uploadedto"
            try:
                servers_module = __import__("servers."+server)
                title = "Enlace encontrado en "+server+" ["+quality+"]"
                if "Español.png" in match: title += " [COLOR sandybrown][CAST][/COLOR]"
                if "VOS.png" in match: title += " [COLOR green][VOSE][/COLOR]"
                if "Latino.png" in match: title += " [COLOR red][LAT][/COLOR]"
                if "VO.png" in match: title += " [COLOR blue][V.O][/COLOR]"
                itemlist.append( Item(channel=__channel__, action="play", title=title , url=url , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=item.fanart, plot=item.plot, folder=True) )
            except:
                pass

    if len(itemlist) == 0: 
        itemlist.append( Item(channel=__channel__, action="", title="No se ha encontrado ningún enlace" , url="" , thumbnail="", fanart=item.fanart, folder=False) )
    else:
        if config.get_library_support() and item.category == "":
            itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir enlaces a la biblioteca[/COLOR]", url=item.url, action="add_pelicula_to_library", fulltitle=item.title.split(" [")[0], show=item.title))
    return itemlist


def play(item):
    logger.info("pelisalacarta.channels.verseriesynovelas play")
    itemlist = []
    data = anti_cloudflare(item.url)
    if "Redireccionando" in data: data = anti_cloudflare(item.url)
    enlace = scrapertools.find_single_match(data, 'class="btn" href="([^"]+)"')
    location = anti_cloudflare(enlace, location=True)
    enlaces = servertools.findvideos(data=location)
    if len(enlaces)> 0:
        titulo = "Enlace encontrado en "+enlaces[0][0]
        itemlist.append( Item(channel=__channel__, action="play", server=enlaces[0][2], title=titulo , url=enlaces[0][1] , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=item.fanart, plot=item.plot, folder=False) )
    return itemlist


def info(title):
    logger.info("pelisalacarta.verseriesynovelas info")
    infolabels={}
    plot={}
    try:
        from core.tmdb import Tmdb
        otmdb= Tmdb(texto_buscado=title, tipo= "tv")
        infolabels['plot'] = otmdb.get_sinopsis()
        infolabels['year']= otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        if otmdb.get_poster() != "": thumbnail = otmdb.get_poster()
        else: thumbnail = ""
        fanart=otmdb.get_backdrop()
        plot['infoLabels']=infolabels
        return plot, fanart, thumbnail
    except:
        pass

def infoepi(otmdb, episode, sinopsis=""):
    logger.info("pelisalacarta.verseriesynovelas infoepi")
    infolabels={}
    plot={}
    try:
        infolabels['season'] = re.split("×|x", episode)[0]
        infolabels['episode'] = re.split("×|x", episode)[1]
        episodio = otmdb.get_episodio(infolabels['season'], infolabels['episode'])
        if episodio["episodio_sinopsis"] == "":
            if sinopsis != "":
                infolabels['plot'] = sinopsis
            else:
                infolabels['plot'] = otmdb.get_sinopsis()
        else:
            infolabels['plot'] = episodio["episodio_sinopsis"]
        if episodio["episodio_titulo"] != "":
            infolabels['title'] =  episodio["episodio_titulo"]
        infolabels['year']= otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        fanart=otmdb.get_backdrop()
        if episodio["episodio_imagen"] == "":
            thumbnail = otmdb.get_poster()
        else:
            thumbnail = episodio["episodio_imagen"]
        infolabels['mediatype'] = "episode"
        plot['infoLabels']=infolabels
        return plot, fanart, thumbnail
    except:
        pass

def anti_cloudflare(url, location=False):
    # global headers
    respuesta = ""
    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
        if resp_headers.has_key('location'): respuesta = resp_headers['location']
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        resp = scrapertools.get_headers_from_response(host + '/' + resp_headers['refresh'][7:], headers=headers)
        resp_headers = dict(resp_headers)
        if resp_headers.has_key('islocation'): respuesta = resp_headers['islocation']

    if not location:
        return scrapertools.cache_page(url, headers=headers)
    else:
        return respuesta
