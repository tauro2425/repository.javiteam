# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Descargasmix
# Por SeiTaN, robalo y Cmos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urllib
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "descargasmix"
__category__ = "A"
__type__ = "generic"
__title__ = "Descargasmix"
__language__ = "ES"

DEBUG = config.get_setting("debug")

DEFAULT_HEADERS = [["User-Agent","Magic Browser"]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.descargasmix mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Películas"      , action="lista", thumbnail= "http://i.imgur.com/tBTqIlV.jpg?1", fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append( Item(channel=__channel__, title="Series"         , action="entradas", url="http://descargasmix.net/series/", thumbnail= "http://i.imgur.com/tBTqIlV.jpg?1", fanart="http://i.imgur.com/9loVksV.png"))
    itemlist.append( Item(channel=__channel__, title="Documentales"   , action="entradas", url="http://descargasmix.net/documentales/", thumbnail= "http://i.imgur.com/tBTqIlV.jpg?1", fanart="http://i.imgur.com/Q7fsFI6.png"))
    itemlist.append( Item(channel=__channel__, title="Anime"          , action="entradas", url="http://descargasmix.net/anime/", thumbnail= "http://i.imgur.com/tBTqIlV.jpg?1", fanart="http://i.imgur.com/whhzo8f.png"))
    itemlist.append( Item(channel=__channel__, title="Deportes"       , action="entradas", url="http://descargasmix.net/deportes/", thumbnail= "http://i.imgur.com/tBTqIlV.jpg?1", fanart="http://i.imgur.com/ggFFR8o.png"))
    itemlist.append( Item(channel=__channel__, title="Buscar..."      , action="search"  , thumbnail= "http://i.imgur.com/tBTqIlV.jpg?1"))
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.descargasmix search")
    item.url= "http://descargasmix.net/?s=" + texto
    itemlist = busqueda(item)
    return itemlist

def busqueda(item):
    logger.info("pelisalacarta.channels.descargasmix busqueda")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    bloque = scrapertools.find_single_match(data, '<div id="content" role="main">(.*?)<div id="sidebar" role="complementary">')
    patron = '<a class="clip-link".*?href="([^"]+)".*?<img alt="([^"]+)" src="([^"]+)"'
    patron += '.*?<p class="stats">(.*?)</p>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail,scrapedcat in matches:
        scrapedthumbnail = "http:"+scrapedthumbnail.replace("-129x180","")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        if ("Películas" in scrapedcat) | ("Documentales" in scrapedcat):
            titulo = scrapedtitle.split("[")[0]
            itemlist.append( Item(channel=__channel__, action='findvideos', title= scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, fulltitle=titulo, context = "0", contentTitle=titulo,folder=True) )
        else:
            itemlist.append( Item(channel=__channel__, action='episodios', title= scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, fulltitle=scrapedtitle, context = "2", contentTitle=scrapedtitle, folder=True) )

    patron = '<a class="nextpostslink".*?href="([^"]+)"'
    matches = scrapertools.find_single_match(data, patron)
    if len(matches) > 0:
        npage = scrapertools.find_single_match(matches,"page/(.*?)/")
        if DEBUG: logger.info("url=["+matches+"]")
        itemlist.append( Item(channel=__channel__, action='busqueda', title= "Página "+npage , url=matches ,folder=True) )

    return itemlist
	
def lista(item):
    logger.info("pelisalacarta.channels.descargasmix lista")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades"      , action="entradas"    , url="http://descargasmix.net/peliculas", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="Estrenos"       , action="entradas"    , url="http://descargasmix.net/peliculas/estrenos", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="Dvdrip"         , action="entradas"    , url="http://descargasmix.net/peliculas/dvdrip", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="HD (720p/1080p)", action="entradas"    , url="http://descargasmix.net/peliculas/hd", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="HDRIP"          , action="entradas"    , url="http://descargasmix.net/peliculas/hdrip", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="Latino"         , action="entradas"    , url="http://descargasmix.net/peliculas/latino-peliculas", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="VOSE"           , action="entradas"    , url="http://descargasmix.net/peliculas/subtituladas", thumbnail= item.thumbnail, fanart=item.fanart))
    itemlist.append( Item(channel=__channel__, title="3D"             , action="entradas"    , url="http://descargasmix.net/peliculas/3d", thumbnail= item.thumbnail, fanart=item.fanart))
    return itemlist

def entradas(item):
    logger.info("pelisalacarta.channels.descargasmix entradas")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    bloque = scrapertools.find_single_match(data, '<div id="content" role="main">(.*?)<div id="sidebar" role="complementary">')
    contenido = ["series","deportes","anime"]
    c_match = [True for match in contenido if match in item.url]
    #Patron dependiendo del contenido
    if True in c_match:
        patron = '<a class="clip-link".*?href="([^"]+)".*?<img alt="([^"]+)" src="([^"]+)"'
        patron += '.*?<span class="overlay(|[^"]+)">'
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for scrapedurl, scrapedtitle, scrapedthumbnail,scrapedinfo in matches:
            if scrapedinfo != "": scrapedinfo = " [[COLOR red]"+scrapedinfo.replace(" ","").replace("-", " ").capitalize()+"[/COLOR]]"
            titulo = scrapedtitle+scrapedinfo	
            titulo = scrapertools.decodeHtmlentities(titulo)
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
            scrapedthumbnail = "http:"+scrapedthumbnail.replace("-129x180","")
            scrapedthumbnail = scrapedthumbnail.rsplit("/",1)[0]+"/"+urllib.quote(scrapedthumbnail.rsplit("/",1)[1])
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append( Item(channel=__channel__, action='episodios', title= titulo , url=scrapedurl , thumbnail=scrapedthumbnail, fanart=item.fanart, fulltitle=scrapedtitle, context = "2", contentTitle=scrapedtitle, folder=True) )
    else:
        patron = '<a class="clip-link".*?href="([^"]+)".*?<img alt="([^"]+)" src="([^"]+)"'
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            titulo = scrapertools.decodeHtmlentities(scrapedtitle)
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.split("[")[0])
            scrapedthumbnail = "http:"+scrapedthumbnail.replace("-129x180","")
            scrapedthumbnail = scrapedthumbnail.rsplit("/",1)[0]+"/"+urllib.quote(scrapedthumbnail.rsplit("/",1)[1])
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append( Item(channel=__channel__, action='findvideos', title= titulo , url=scrapedurl , thumbnail=scrapedthumbnail, fanart=item.fanart, fulltitle=scrapedtitle, context = "0", contentTitle=scrapedtitle, folder=True) )
    #Paginación
    patron = '<a class="nextpostslink".*?href="([^"]+)"'
    matches = scrapertools.find_single_match(data, patron)
    if len(matches) > 0:
        npage = scrapertools.find_single_match(matches,"page/(.*?)/")
        if DEBUG: logger.info("url=["+matches+"]")
        itemlist.append( Item(channel=__channel__, action='entradas', title= "Página "+npage , url=matches , fanart=item.fanart, folder=True) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.descargasmix episodios")
    itemlist = []
    fanart = item.fanart
    thumbnail = item.thumbnail
    if item.category == "":
        try:
            from core.tmdb import Tmdb
            otmdb= Tmdb(texto_buscado=item.fulltitle, tipo="tv")
        except:
            pass
    data = scrapertools.cachePage(item.url)
    patron = '(<ul class="menu" id="seasons-list">.*?<div class="section-box related-posts">)'
    bloque = scrapertools.find_single_match(data, patron)
    patron = '<strong>(.*?)</strong>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedtitle in matches:
        if item.category == "":
            try:
                item.plot, fanart, thumbnail = infoepi(otmdb, scrapedtitle)
            except:
                pass
        scrapedtitle = item.fulltitle+" "+scrapedtitle.strip()
        itemlist.append( Item(channel=__channel__, action="epienlaces", title=scrapedtitle, fulltitle = item.fulltitle, url=item.url , thumbnail=thumbnail , fanart=fanart, plot=str(item.plot), context = "2", contentTitle=item.fulltitle, show=item.fulltitle, folder=True ))

    itemlist.sort(key=lambda item: item.title, reverse=True)

    if config.get_library_support():
        itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir esta serie a la biblioteca[/COLOR]", url=item.url, action="add_serie_to_library", extra="episodios", fulltitle=item.fulltitle, show=item.fulltitle))
    return itemlist

def epienlaces(item):
    logger.info("pelisalacarta.channels.descargasmix epienlaces")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")

    #Bloque de enlaces
    delimitador = item.title.replace(item.show,"")
    patron = delimitador+'\s*</strong>(.*?)(?:</strong>|<div class="section-box related-posts")'
    bloque = scrapertools.find_single_match(data, patron)
     
    logger.info(bloque)
    patron = '<div class="episode-server">.*?href="([^"]+)"'
    patron += '.*?data-server="([^"]+)"'
    patron += '.*?<div style="float:left;width:140px;">(.*?)</div>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedserver, scrapedcalidad in matches:
        if scrapedserver == "ul": scrapedserver = "uploadedto"
        if scrapedserver == "streamin": scrapedserver = "streaminto"
        titulo = scrapedserver.capitalize()+" ["+scrapedcalidad+"]"
        #Enlaces descarga
        if scrapedserver == "magnet":
            titulo = titulo.replace("Magnet", "[COLOR green][Enlace en Torrent][/COLOR]")
            itemlist.insert(0, Item(channel=__channel__, action="play", title=titulo, server="torrent", url=scrapedurl , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=item.fanart, plot=item.plot, folder=False) )
        else:
            mostrar_server= True
            if config.get_setting("hidepremium")=="true":
                mostrar_server= servertools.is_server_enabled (scrapedserver)
            if mostrar_server:
                try:
                    servers_module = __import__("servers."+scrapedserver)
                    if "http://descargasmix" in scrapedurl:
                        DEFAULT_HEADERS.append( ["Referer", item.url] )
                        data = scrapertools.cache_page(scrapedurl, headers=DEFAULT_HEADERS)
                        scrapedurl = scrapertools.find_single_match(data, 'iframe src="([^"]+)"')
                         
                    enlaces = servertools.findvideos(data=scrapedurl)
                    if len(enlaces)> 0:
                        for enlace in enlaces:
                            titulo = "Enlace encontrado en [COLOR sandybrown]"+enlaces[0][0]+"[/COLOR] ["+scrapedcalidad+"]"
                            itemlist.append( Item(channel=__channel__, action="play", server=enlaces[0][2], title=titulo , url=enlaces[0][1] , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=item.fanart, plot=item.plot, folder=False) )
                except:
                    pass
    if config.get_library_support() and item.category == "":
        itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir enlaces a la biblioteca[/COLOR]", url=item.url+"|", action="add_pelicula_to_library", extra="epienlaces", fulltitle=item.title, show=item.title))

    return itemlist


def findvideos(item):
    logger.info("pelisalacarta.channels.descargasmix findvideos")
    if item.category == "Series" or item.show!="": return epienlaces(item)
    itemlist = []
    data = scrapertools.cachePage(item.url)

    fanart = item.fanart
    sinopsis = scrapertools.find_single_match(data, '<strong>SINOPSIS</strong>:(.*?)</p>')
    if item.category == "":
        try:
            sinopsis, fanart = info(item.fulltitle, "movie", sinopsis)
        except:
            pass
    #Patron torrent
    patron = 'class="separate3 magnet".*?href="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl in matches:
        title = urllib.unquote(scrapedurl)
        try:
            if item.fulltitle != "": titulo = item.fulltitle.strip().rsplit(" ",1)[1]
            else: titulo = item.title.strip().rsplit(" ",1)[1]
        except:
            if item.fulltitle != "": titulo = item.fulltitle.strip()
            else: titulo = item.title.strip()

        title = "["+scrapertools.find_single_match(title, titulo+"(?:\.|)(.*?)(?:\.|[wW])")+"]"
        itemlist.append( Item(channel=__channel__, action="play", server="torrent", title="[COLOR green][Enlace en Torrent][/COLOR] "+title , fulltitle = item.fulltitle, url=scrapedurl , thumbnail=item.thumbnail , fanart=fanart, plot=str(sinopsis) , context = "0", contentTitle=item.fulltitle, folder=False) )
    
    #Patron online
    data_online = scrapertools.find_single_match(data, 'Enlaces para ver online(.*?)<div class="section-box related-posts">')
    if len(data_online)> 0:
        patron = 'dm\(c.a\(\'([^\']+)\''
        matches = scrapertools.find_multiple_matches(data_online, patron)
        for code in matches:
            enlace = dm(code)
            enlaces = servertools.findvideos(data=enlace)
            titulo = "Enlace encontrado en [COLOR sandybrown]"+enlaces[0][0]+"[/COLOR]"
            if len(enlaces)> 0:
                itemlist.append( Item(channel=__channel__, action="play", server=enlaces[0][2], title=titulo, url=enlaces[0][1] , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=fanart, plot=str(sinopsis) , context = "0", contentTitle=item.fulltitle, viewmode="movie_with_plot", folder=False) )

    #Patron descarga
    data_descarga = scrapertools.find_single_match(data, 'Enlaces de descarga(.*?)<script>')
    patron = '<div class="fondoenlaces".*?id=".*?_([^"]+)".*?textContent=nice=dm\(c.a\(\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data_descarga, patron)
    for scrapedserver, scrapedurl in matches:
        if (scrapedserver == "ul") | (scrapedserver == "uploaded"): scrapedserver = "uploadedto"
        titulo = scrapedserver.capitalize()
        if titulo == "Magnet":continue
        mostrar_server= True
        if config.get_setting("hidepremium")=="true":
            mostrar_server= servertools.is_server_enabled (scrapedserver)
        if mostrar_server:
            try:
                servers_module = __import__("servers."+scrapedserver)
                #Saca numero de enlaces
                patron = "(dm\(c.a\('"+scrapedurl.replace("+","\+")+"'.*?)</div>"
                data_enlaces = scrapertools.find_single_match(data_descarga, patron)
                patron = 'dm\(c.a\(\'([^\']+)\''
                matches_enlaces = scrapertools.find_multiple_matches(data_enlaces,patron)
                numero = str(len(matches_enlaces))
                if item.category == "": itemlist.append( Item(channel=__channel__, action="enlaces", server="", title=titulo+" - Nº enlaces:"+numero , url=item.url , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=fanart, plot=str(sinopsis) , extra=scrapedurl, context = "0", contentTitle=item.fulltitle, viewmode="movie_with_plot", folder=True) )
            except:
                pass

    if config.get_library_support() and item.category == "":
        itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir enlaces a la biblioteca[/COLOR]", url=item.url, action="add_pelicula_to_library", extra="findvideos", fulltitle=item.fulltitle.strip()))
    return itemlist
	
def enlaces(item):
    logger.info("pelisalacarta.channels.descargasmix enlaces")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    #Bloque de enlaces
    patron = "(dm\(c.a\('"+item.extra.replace("+","\+")+"'.*?)</div>"
    data_enlaces = scrapertools.find_single_match(data,patron)
    patron = 'dm\(c.a\(\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data_enlaces, patron)
    numero = len(matches)
    for code in matches:
        enlace = dm(code)
        enlaces = servertools.findvideos(data=enlace)
        if len(enlaces)> 0:
            for link in enlaces:
                if "/folder/" in enlace: titulo = link[0]
                else:
                    titulo = item.title.split("-")[0]+" - Enlace "+str(numero)
                    numero -= 1
                itemlist.append( Item(channel=__channel__, action="play", server=link[2], title=titulo , url=link[1] , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=item.fanart, plot=item.plot, folder=False) )
    itemlist.sort(key=lambda item: item.title)
    return itemlist

def dm(h):
    import base64
    h = base64.decodestring(h)

    copies = ""
    i = 0
    while i < len(h):
        copies += chr(ord(h[i]) ^ 123 * ~~ True)
        i += 1

    return copies
	

def info(title, type, sinopsis):
    logger.info("pelisalacarta.descargasmix info")
    infolabels={}
    plot={}
    try:
        from core.tmdb import Tmdb
        otmdb= Tmdb(texto_buscado=title, tipo= type)
        if otmdb.get_sinopsis() == "": infolabels['plot'] = sinopsis
        else: infolabels['plot'] = otmdb.get_sinopsis()
        infolabels['year']= otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        fanart=otmdb.get_backdrop()
        plot['infoLabels']=infolabels
        return plot, fanart
    except:
        pass

def infoepi(otmdb, episode):
    logger.info("pelisalacarta.descargasmix infoepi")
    infolabels={}
    plot={}
    try:
        infolabels['season'] = episode.split("x")[0]
        infolabels['episode'] = episode.split("x")[1]
        episodio = otmdb.get_episodio(infolabels['season'], infolabels['episode'])
        if episodio["episodio_sinopsis"] == "": infolabels['plot'] = otmdb.get_sinopsis()
        else: infolabels['plot'] = episodio["episodio_sinopsis"]
        infolabels['year']= otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        fanart=otmdb.get_backdrop()
        if episodio["episodio_imagen"] == "": thumbnail = otmdb.get_poster()
        else: thumbnail = episodio["episodio_imagen"]
        plot['infoLabels']=infolabels
        return plot, fanart, thumbnail
    except:
        pass
