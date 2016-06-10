# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Allpeliculas
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import string
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "allpeliculas"
__category__ = "A"
__type__ = "generic"
__title__ = "Allpeliculas"
__language__ = "ES"

DEBUG = config.get_setting("debug")
IDIOMAS = {"Castellano":"CAST","Latino":"LAT","Subtitulado":"VOSE","Ingles":"VO"}

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.allpeliculas mainlist")
    itemlist = []
    itemlist.append(Item(channel=__channel__, title="Películas" , action="lista", url="http://allpeliculas.co/Movies/fullView/1/0/&ajax=1", thumbnail= "http://i.imgur.com/aWCDWtn.png", fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(Item(channel=__channel__, title="Series"      , action="lista", url="http://allpeliculas.co/Movies/fullView/1/86/?ajax=1&withoutFilter=1", thumbnail= "http://i.imgur.com/aWCDWtn.png", fanart="http://i.imgur.com/9loVksV.png", extra="tv"))
    itemlist.append(Item(channel=__channel__, title="Géneros"      , action="subindice", thumbnail= "http://i.imgur.com/aWCDWtn.png", fanart="http://i.imgur.com/ymazCWq.jpg"))
    itemlist.append(Item(channel=__channel__, title="Índices"      , action="indices", thumbnail= "http://i.imgur.com/aWCDWtn.png", fanart="http://i.imgur.com/c3HS8kj.png"))
    itemlist.append(Item(channel=__channel__, title="Buscar..."      , action="search", thumbnail= "http://i.imgur.com/aWCDWtn.png"))
    return itemlist

def search(item, texto):
    logger.info("pelisalacarta.channels.allpeliculas search")
    item.url = "http://allpeliculas.co/Search/advancedSearch?searchType=movie&movieName=" + texto + "&ajax=1"
    try:
        itemlist = busqueda(item)
        if item.title == "Buscar..." and len(itemlist) == 0:
            itemlist.append(Item(channel=__channel__, title="[COLOR sandybrown][B]Búsqueda sin resultado[/B][/COLOR]" , thumbnail= "http://i.imgur.com/aWCDWtn.png"))
        return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def busqueda(item):
    logger.info("pelisalacarta.channels.allpeliculas busqueda")
    itemlist = []
    infolabels = {}
    plot = {}
    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    patron = '<img class="poster" src="([^"]+)".*?'
    patron += '<div class="vote-div-count".*?>(.*?)/.*?'
    patron += '<a class="movie-list-link" href="([^"]+)" title="([^"]+)".*?'
    patron += 'Year:</b> (.*?) </p>.*?Género:</b> (.*?)</p>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for thumb, vote, url , title, year, genre in matches:
        url = "http://allpeliculas.co"+url+"&ajax=1"
        url= url.replace("#","")
        thumb = thumb.replace("/105/","/400/").replace("/141/","/600/").replace(" ","%20")
        titulo = title+" ("+year+")"
        infolabels['year'] = year
        infolabels['genre'] = genre
        infolabels['plot'] = ""
        infolabels['rating'] = vote
        plot['infoLabels'] = infolabels
        if "Series" not in genre:
            itemlist.append(Item(channel=__channel__, action="findvideos", title=titulo , fulltitle = title, url=url , thumbnail=thumb , plot=str(plot), fanart= item.fanart, context = "0", contentTitle=title, folder=True) )
        else:
            itemlist.append(Item(channel=__channel__, action="temporadas", title=titulo , fulltitle = title, url=url , thumbnail=thumb , plot=str(plot), fanart= item.fanart, context = "2", contentTitle=title, folder=True) )

    #Paginacion
    patron = 'class="pagination-active".*?href="([^"]+)">(.*?)</a>'
    matches = scrapertools.find_single_match(data, patron)
    if len(matches) > 0:
        url = matches[0]+"&ajax=1"
        url = url.replace("#","")
        itemlist.append(Item(channel=__channel__, action="busqueda", title="Página "+matches[1] , url=url , folder=True) )

    return itemlist

def indices(item):
    logger.info("pelisalacarta.channels.allpeliculas indices")
    itemlist = []
    itemlist.append(Item(channel=__channel__, title="Alfabético"      , action="subindice", thumbnail=item.thumbnail , fanart=item.fanart))
    itemlist.append(Item(channel=__channel__, title="Por idioma"      , action="subindice", thumbnail=item.thumbnail , fanart=item.fanart))
    itemlist.append(Item(channel=__channel__, title="Por valoración"      , action="lista", url="http://allpeliculas.co/Movies/fullView/1/0/rating:imdb|date:1900-2016|alphabet:all|?ajax=1&withoutFilter=1", thumbnail=item.thumbnail , fanart=item.fanart))
    itemlist.append(Item(channel=__channel__, title="Por año"      , action="subindice", thumbnail=item.thumbnail , fanart=item.fanart))
    itemlist.append(Item(channel=__channel__, title="Por calidad"      , action="subindice", thumbnail=item.thumbnail , fanart=item.fanart))
    return itemlist

def lista(item):
    logger.info("pelisalacarta.channels.allpeliculas lista")
    itemlist = []
    infolabels = {}
    plot = {}
    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)

    bloque = scrapertools.find_single_match(data, '<div class="movies-block-main"(.*?)<div class="movies-long-pagination"')
    patron = '<div class="thumb"><img src="([^"]+)".*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<div class="imdb"><span>(.*?)</span>.*?'
    patron += '<span>Year.*?">(.*?)</a>.*?<span>(?:Género|Genre).*?<span>(.*?)</span>.*?'
    patron += '<span>Language.*?<span>(.*?)</span>.*?'
    patron += '<div class="info-full-text".*?>(.*?)<.*?'
    patron += '<div class="views">(.*?)<.*?<div class="movie-block-title".*?>(.*?)<'
    if len(bloque) > 0: matches = scrapertools.find_multiple_matches(bloque, patron)
    else: matches = scrapertools.find_multiple_matches(data, patron)
    for thumb, url , vote, year, genre, idioma, sinopsis, calidad, title in matches:
        url += "&ajax=1"
        url = url.replace("#","")
        thumb = thumb.replace("/157/","/400/").replace("/236/","/600/").replace(" ","%20")
        idioma = idioma.replace(" ","").split(",")
        idioma.sort()
        titleidioma = "[COLOR sandybrown]["
        for i in range(0,len(idioma)):
            if i != len(idioma)-1:
                titleidioma += IDIOMAS.get(idioma[i])+"/"
            else:
                titleidioma += IDIOMAS.get(idioma[i])+"][/COLOR]"
        titulo = title+" "+titleidioma+" ["+calidad+"] "+"("+year+")"
        infolabels['plot'] = sinopsis
        infolabels['year'] = year
        infolabels['genre'] = genre
        infolabels['rating'] = vote
        plot['infoLabels'] = infolabels
        if (item.extra != "tv") | ("Series" not in genre):
            itemlist.append(Item(channel=__channel__, action="findvideos", title=titulo , fulltitle = title, url=url , thumbnail=thumb , plot=str(plot), fanart= item.fanart, context = "0", contentTitle=title, folder=True) )
        else:
            itemlist.append(Item(channel=__channel__, action="temporadas", title=titulo , fulltitle = title, url=url , thumbnail=thumb , plot=str(plot), fanart= item.fanart, context = "2", contentTitle=title, folder=True) )

    #Paginacion
    patron = 'class="pagination-active".*?href="([^"]+)">(.*?)</a>'
    matches = scrapertools.find_single_match(data, patron)
    if len(matches) > 0:
        url = matches[0]+"&ajax=1"
        url = url.replace("#","")
        if item.extra != "tv":
            itemlist.append(Item(channel=__channel__, action="lista", title="Página "+matches[1] , url=url , folder=True) )
        else:
            itemlist.append(Item(channel=__channel__, action="lista", title="Página "+matches[1] , url=url , extra="tv", folder=True) )

    return itemlist

def subindice(item):
    logger.info("pelisalacarta.channels.allpeliculas subindice")
    itemlist = []
    url_base = "http://allpeliculas.co/Movies/fullView/1/0/date:1900-2016|alphabet:all|?ajax=1&withoutFilter=1"
    indice_genero, indice_alfa, indice_idioma, indice_year, indice_calidad = dict_indices()
    if item.title == "Géneros":
        for key, value in indice_genero.items():
            url = url_base.replace("/0/","/"+key+"/")
            itemlist.append(Item(channel=__channel__, action="lista", title=value , url=url, thumbnail=item.thumbnail ,fanart= item.fanart, folder=True) )
            itemlist.sort(key=lambda item: item.title)

    elif item.title == "Alfabético":
        for i in range(len(indice_alfa)):
            url = url_base.replace(":all", ":"+indice_alfa[i])
            itemlist.append(Item(channel=__channel__, action="lista", title=indice_alfa[i] , url=url, thumbnail=item.thumbnail ,fanart= item.fanart, folder=True) )

    elif item.title == "Por idioma":
        for key, value in indice_idioma.items():
            url = url_base.replace("2016|","2016|language:"+key)
            itemlist.append(Item(channel=__channel__, action="lista", title=value , url=url, thumbnail=item.thumbnail ,fanart= item.fanart, folder=True) )
            itemlist.sort(key=lambda item: item.title)

    elif item.title == "Por año":
        for i in range(len(indice_year)):
            year = indice_year[i]
            url = url_base.replace("1900-2016",year+"-"+year)
            itemlist.append(Item(channel=__channel__, action="lista", title=year , url=url, thumbnail=item.thumbnail ,fanart= item.fanart, folder=True) )

    elif item.title == "Por calidad":
        for key, value in indice_calidad.items():
            url = "http://allpeliculas.co/Search/advancedSearch?searchType=movie&movieName=&movieDirector=&movieGenre=&movieActor=&movieYear=&language=&movieTypeId="+key+"&ajax=1"
            itemlist.append(Item(channel=__channel__, action="busqueda", title=value , url=url, thumbnail=item.thumbnail ,fanart= item.fanart, folder=True) )
            itemlist.sort(key=lambda item: item.title)

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.allpeliculas findvideos")
    itemlist = []
    sinopsis = item.plot
    fanart = item.fanart
    #Rellena diccionarios idioma y calidad
    idiomas_videos, calidad_videos = dict_videos()

    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    try:
        sinopsis, fanart = info(item.fulltitle, "movie", scrapertools.find_single_match(sinopsis,"plot:'([^']+)'"))
    except:
        pass
    #Enlaces Online
    patron = '<span class="movie-online-list" id_movies_types="([^"]+)".*?id_lang="([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for calidad, language, url in matches:
         enlaces = servertools.findvideos(data=url)
         if len(enlaces)> 0:
             idioma = IDIOMAS.get(idiomas_videos.get(language))
             titulo = "Enlace encontrado en [COLOR green][B]"+enlaces[0][0]+"[/B][/COLOR] [COLOR sandybrown]["+idioma+"][/COLOR] ["+calidad_videos.get(calidad)+"]"
             servidor = enlaces[0][2]
             itemlist.append(Item(channel=__channel__, action="play", server=servidor, title=titulo , url=enlaces[0][1] , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=fanart, plot=str(sinopsis) , extra=idioma, folder=False) )

    #Enlace Descarga
    patron = '<span class="movie-downloadlink-list" id_movies_types="([^"]+)".*?id_lang="([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for calidad, language, url in matches:
        mostrar_server = True
        enlaces = servertools.findvideos(data=url)
        if len(enlaces)> 0:
            servidor = enlaces[0][2]
            if config.get_setting("hidepremium")=="true":
                mostrar_server = servertools.is_server_enabled(servidor)
            if mostrar_server:
                idioma = IDIOMAS.get(idiomas_videos.get(language))
                titulo = "Enlace encontrado en [COLOR blue][B]"+enlaces[0][0]+"[/B][/COLOR] [COLOR sandybrown]["+idioma+"][/COLOR] ["+calidad_videos.get(calidad)+"]"
                itemlist.append(Item(channel=__channel__, action="play", server=servidor, title=titulo , url=enlaces[0][1] , fulltitle = item.fulltitle, thumbnail=item.thumbnail , fanart=fanart, plot=str(sinopsis) , extra=idioma, folder=False) )

    itemlist.sort(key=lambda item:(item.extra, item.server))
    if len(itemlist) > 0 and item.category == "" or item.category == "Buscador":
        if config.get_library_support():
            itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir enlaces a la biblioteca[/COLOR]", url=item.url, action="add_pelicula_to_library", fulltitle=item.fulltitle, show=item.fulltitle))
    return itemlist

def temporadas(item):
    logger.info("pelisalacarta.channels.allpeliculas temporadas")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    sinopsis = item.plot
    fanart = item.fanart
    try:
        sinopsis, fanart = info(item.fulltitle, "tv", scrapertools.find_single_match(sinopsis,"plot:'([^']+)'"))
    except:
        pass
    patron = '<a class="movie-season" data-id="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    matches = list(set(matches))
    for scrapedtitle in matches:
        itemlist.append(Item(channel=__channel__, action="findvideostv", title="Temporada "+scrapedtitle , fulltitle = item.fulltitle, url=item.url , thumbnail=item.thumbnail , fanart=fanart, plot=str(sinopsis), context = "2", contentTitle=item.fulltitle, folder=True) )

    itemlist.sort(key=lambda item: item.title)
    return itemlist

def findvideostv(item):
    logger.info("pelisalacarta.channels.allpeliculas findvideostv")
    itemlist = []
    season = item.title.split(" ")[1]
    thumbnail = item.thumbnail
    #Rellena diccionarios idioma y calidad
    idiomas_videos, calidad_videos = dict_videos()

    data = scrapertools.cachePage(item.url)
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    try:
        from core.tmdb import Tmdb
        otmdb= Tmdb(texto_buscado=item.fulltitle, tipo="tv")
    except:
        pass
    #Enlaces Online
    patron = '<span class="movie-online-list" id_movies_types="([^"]+)".*?episode="([^"]+)" season="'+season+'" id_lang="([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, episode, language, url in matches:
         enlaces = servertools.findvideos(data=url)
         if len(enlaces)> 0:
             idioma = IDIOMAS.get(idiomas_videos.get(language))
             titulo = "[COLOR sandybrown][B]Episodio "+episode+"[/B][/COLOR] "
             titulo += "Enlace encontrado en [COLOR green][B]"+enlaces[0][0]+"[/B][/COLOR] [COLOR magenta]["+idioma+"][/COLOR] ["+calidad_videos.get(quality)+"]"
             servidor = enlaces[0][2]
             try:
                 item.plot, thumbnail = infoepi(otmdb, season, episode)
             except:
                 pass
             itemlist.append(Item(channel=__channel__, action="play", server=servidor, title=titulo, url=enlaces[0][1], fulltitle = item.fulltitle, thumbnail=thumbnail, fanart=item.fanart, plot=str(item.plot), extra=episode, folder=False))

    #Enlace Descarga
    patron = '<span class="movie-downloadlink-list" id_movies_types="([^"]+)".*?episode="([^"]+)" season="'+season+'" id_lang="([^"]+)".*?online-link="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, episode, language, url in matches:
        mostrar_server = True
        enlaces = servertools.findvideos(data=url)
        if len(enlaces)> 0:
            servidor = enlaces[0][2]
            if config.get_setting("hidepremium")=="true":
                mostrar_server = servertools.is_server_enabled(servidor)
            if mostrar_server:
                idioma = IDIOMAS.get(idiomas_videos.get(language))
                titulo = "[COLOR sandybrown][B]Episodio "+episode+"[/B][/COLOR] "
                titulo += "Enlace encontrado en [COLOR green][B]"+enlaces[0][0]+"[/B][/COLOR] ["+idioma+"] ["+calidad_videos.get(quality)+"]"
                try:
                    item.plot, thumbnail = infoepi(otmdb, season, episode)
                except:
                    pass
                itemlist.append(Item(channel=__channel__, action="play", server=servidor, title=titulo , url=enlaces[0][1] , fulltitle = item.fulltitle, thumbnail=thumbnail , fanart=item.fanart, plot=str(item.plot) , extra=episode, folder=False) )

    itemlist.sort(key=lambda item:(int(item.extra), item.title))
    return itemlist

def dict_videos():
    idiomas_videos = {}
    calidad_videos = {}
    data = scrapertools.cachePage("http://allpeliculas.co/Search/advancedSearch&ajax=1")
    data = data.replace("\n","").replace("\t", "")
    bloque_idioma = scrapertools.find_single_match(data, '<select name="language".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_idioma, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        idiomas_videos [key1] = key2.capitalize()
    bloque_calidad = scrapertools.find_single_match(data, '<select name="movieTypeId".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_calidad, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        calidad_videos [key1] = key2

    return idiomas_videos, calidad_videos

def dict_indices():
    indice_genero = {}
    indice_alfa = list(string.ascii_uppercase)
    indice_alfa.append("0-9")
    indice_idioma = {}
    indice_year = []
    indice_calidad = {}
    data = scrapertools.cachePage("http://allpeliculas.co/Search/advancedSearch&ajax=1")
    data = data.replace("\n","").replace("\t", "")
    data = scrapertools.decodeHtmlentities(data)
    bloque_genero = scrapertools.find_single_match(data, '<select name="movieGenre".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_genero, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        if key2 != "Series":
            if key2 == "Mystery": key2= "Misterio"
            indice_genero [key1] = key2
    bloque_year = scrapertools.find_single_match(data, '<select name="movieYear".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_year, '<option value="([^"]+)"')
    for key1 in matches:
        indice_year.append(key1)
    bloque_idioma = scrapertools.find_single_match(data, '<select name="language".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_idioma, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        if key2 == "INGLES": key2 = "Versión original"
        indice_idioma [key1] = key2.capitalize()

    bloque_calidad = scrapertools.find_single_match(data, '<select name="movieTypeId".*?<option value="" selected(.*?)</select>')
    matches = scrapertools.find_multiple_matches(bloque_calidad, '<option value="([^"]+)" >(.*?)</option>')
    for key1, key2 in matches:
        indice_calidad [key1] = key2

    return indice_genero, indice_alfa, indice_idioma, indice_year, indice_calidad

def info(title, type, sinopsis):
    logger.info("pelisalacarta.allpeliculas info")
    infolabels = {}
    plot = {}
    try:
        from core.tmdb import Tmdb
        otmdb= Tmdb(texto_buscado=title, tipo= type)
        if otmdb.get_sinopsis() == "": infolabels['plot'] = sinopsis
        else: infolabels['plot'] = otmdb.get_sinopsis()
        infolabels['year'] = otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        fanart = otmdb.get_backdrop()
        plot['infoLabels'] = infolabels
        return plot, fanart
    except:
        pass

def infoepi(otmdb, season, episode):
    logger.info("pelisalacarta.allpeliculas infoepi")
    infolabels = {}
    plot = {}
    try:
        infolabels['season'] = season
        infolabels['episode'] = episode
        episodio = otmdb.get_episodio(infolabels['season'], infolabels['episode'])
        if episodio["episodio_sinopsis"] == "": infolabels['plot'] = otmdb.get_sinopsis()
        else: infolabels['plot'] = episodio["episodio_sinopsis"]
        infolabels['year'] = otmdb.result["release_date"][:4]
        infolabels['genre'] = otmdb.get_generos()
        infolabels['rating'] = float(otmdb.result["vote_average"])
        if episodio["episodio_imagen"] == "": thumbnail = otmdb.get_poster()
        else: thumbnail = episodio["episodio_imagen"]
        infolabels['mediatype'] = "episode"
        plot['infoLabels'] = infolabels
        return plot, thumbnail
    except:
        pass
