# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para tvvip
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urllib, unicodedata, sys, time, urllib2, os
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import jsontools

__channel__ = "tvvip"
__category__ = "F,S,D"
__type__ = "generic"
__title__ = "TV-VIP"
__language__ = "ES"

DEBUG = config.get_setting("debug")
host = "http://tv-vip.com"

headers = [
    ["User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"],
    ["Accept-Encoding","gzip, deflate"],
    ["Referer",host]
    ]

header_string = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0&Accept-Encoding=gzip, deflate&Referer=http://tv-vip.com"

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.tvvip mainlist")
    itemlist = []
    data, cloudflare = anti_cloudflare("http://tv-vip.com/json/playlist/home/index.json")
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    itemlist.append( Item(channel=__channel__, title="Películas"         , action="submenu", thumbnail= "http://tv-vip.com/json/playlist/peliculas/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/peliculas/background.jpg"+head, viewmode="movie"))
    itemlist.append( Item(channel=__channel__, title="Series"   , action="submenu", thumbnail= "http://tv-vip.com/json/playlist/series/poster.jpg"+head, fanart="http://tv-vip.com/json/playlist/series/background.jpg"+head))
    itemlist.append( Item(channel=__channel__, title="Versión Original"   , action="entradasconlistas", url="http://tv-vip.com/json/playlist/version-original/index.json", thumbnail= "http://tv-vip.com/json/playlist/version-original/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/version-original/background.jpg"+head))
    itemlist.append( Item(channel=__channel__, title="Documentales"       , action="entradasconlistas", url="http://tv-vip.com/json/playlist/documentales/index.json", thumbnail= "http://tv-vip.com/json/playlist/documentales/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/documentales/background.jpg"+head))
    itemlist.append( Item(channel=__channel__, title="Películas Infantiles"         , action="entradasconlistas", url="http://tv-vip.com/json/playlist/peliculas-infantiles/index.json", thumbnail= "http://tv-vip.com/json/playlist/peliculas-infantiles/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/peliculas-infantiles/background.jpg"+head))
    itemlist.append( Item(channel=__channel__, title="Series Infantiles"         , action="entradasconlistas", url="http://tv-vip.com/json/playlist/series-infantiles/index.json", thumbnail= "http://tv-vip.com/json/playlist/series-infantiles/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/series-infantiles/background.jpg"+head))
    itemlist.append( Item(channel=__channel__, title="Buscar..."      , action="search", thumbnail= "http://i.imgur.com/gNHVlI4.png", fanart="http://i.imgur.com/9loVksV.png"))
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.tvvip search")
    item.url= "http://tv-vip.com/video-prod/s/search?q=%s&n=100" % texto

    try:
        return busqueda(item)
	    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def busqueda(item):
    logger.info("pelisalacarta.channels.tvvip busqueda")
    itemlist = []

    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    for child in data["objectList"]:
        infolabels={}
        plot={}

        infolabels['year']= child['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',','.')
        infolabels['votes'] = child['rateCount']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']

        if 'playListChilds' not in child:
            infolabels['plot'] = child['description']
            type = "repo"
            fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore').decode("utf-8")
            title = child['name']
            infolabels['duration'] = child['duration']	
            if child['height'] < 720: quality = "[B]     [SD][/B]"
            elif child['height'] < 1080: quality = "[B]     [720p][/B]"
            elif child['height'] >= 1080: quality = "[B]     [1080p][/B]"
            if child['year'] != "" : title += " (" + child['year'] + ")"
            title += quality
            action = "findvideos"
        else:
            type = "playlist"
            infolabels['plot'] = "Contiene:\n"+"\n".join(child['playListChilds'])+"\n".join(child['repoChilds'])
            fulltitle = child['id']           
            title = "[COLOR red][LISTA][/COLOR] "+child['id'].replace('-', ' ').capitalize() + " ([COLOR gold]"+str(child['number'])+"[/COLOR])"
            action = "entradasconlistas"
        url = "http://tv-vip.com/json/%s/%s/index.json" % (type, child["id"])
        # Fanart
        if child['hashBackground']: fanart = "http://tv-vip.com/json/%s/%s/background.jpg" % (type, child["id"])
        else: fanart = "http://tv-vip.com/json/%s/%s/thumbnail.jpg" % (type, child["id"])
        # Thumbnail
        if child['hasPoster']: thumbnail = "http://tv-vip.com/json/%s/%s/poster.jpg" % (type, child["id"])
        else: thumbnail = fanart
        thumbnail += head
        fanart += head
        plot['infoLabels']=infolabels
        if type == 'playlist': itemlist.insert(0, Item(channel=__channel__, action='entradasconlistas', title=title , url=url , thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, plot=str(plot), viewmode="movie_with_plot", folder=True) )
        else: itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, contentTitle=fulltitle, context="0", plot=str(plot), viewmode="movie_with_plot", folder=True) )

    return itemlist

def submenu(item):
    logger.info("pelisalacarta.channels.tvvip submenu")
    itemlist = []
    data, cloudflare = anti_cloudflare("http://tv-vip.com/json/playlist/home/index.json")
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    if item.title == "Series":
        itemlist.append( Item(channel=__channel__, title="Nuevos Capítulos"         , action="episodios", url="http://tv-vip.com/json/playlist/nuevos-capitulos/index.json", thumbnail= "http://tv-vip.com/json/playlist/nuevos-capitulos/background.jpg"+head, fanart="http://tv-vip.com/json/playlist/nuevos-capitulos/background.jpg"+head, viewmode="movie"))
        itemlist.append( Item(channel=__channel__, title="Más Vistas"   , action="series", url="http://tv-vip.com/json/playlist/top-series/index.json", thumbnail= "http://tv-vip.com/json/playlist/top-series/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/top-series/background.jpg"+head, contentTitle="Series"))
        itemlist.append( Item(channel=__channel__, title="Últimas Series"   , action="series", url="http://tv-vip.com/json/playlist/novedades/index.json", thumbnail= item.thumbnail, fanart=item.fanart, contentTitle="Series"))
        itemlist.append( Item(channel=__channel__, title="Lista de Series A-Z"       , action="series", url="http://tv-vip.com/json/playlist/series/index.json", thumbnail= item.thumbnail, fanart=item.fanart, contentTitle="Series"))
    else:
        itemlist.append( Item(channel=__channel__, title="Novedades"         , action="entradas", url="http://tv-vip.com/json/playlist/000-novedades/index.json", thumbnail= "http://tv-vip.com/json/playlist/ultimas-peliculas/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/ultimas-peliculas/background.jpg"+head, viewmode="movie"))
        itemlist.append( Item(channel=__channel__, title="Más vistas"   , action="entradas", url="http://tv-vip.com/json/playlist/peliculas-mas-vistas/index.json", thumbnail= "http://tv-vip.com/json/playlist/peliculas-mas-vistas/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/peliculas-mas-vistas/background.jpg"+head))
        itemlist.append( Item(channel=__channel__, title="Categorías"   , action="cat", url="http://tv-vip.com/json/playlist/peliculas/index.json", thumbnail= item.thumbnail, fanart=item.fanart))
        itemlist.append( Item(channel=__channel__, title="Películas 3D"   , action="entradasconlistas", url="http://tv-vip.com/json/playlist/3D/index.json", thumbnail= "http://tv-vip.com/json/playlist/3D/thumbnail.jpg"+head, fanart="http://tv-vip.com/json/playlist/3D/background.jpg"+head))
    return itemlist

def cat(item):
    logger.info("pelisalacarta.channels.tvvip cat")
    itemlist = []

    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    exception = ["peliculas-mas-vistas", "ultimas-peliculas"]
    for child in data["sortedPlaylistChilds"]:
        if child["id"] not in exception:
            url = "http://tv-vip.com/json/playlist/%s/index.json" % child["id"]
            # Fanart
            if child['hashBackground']: fanart = "http://tv-vip.com/json/playlist/%s/background.jpg" % child["id"]
            else: fanart = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            # Thumbnail
            thumbnail = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            thumbnail += head
            fanart += head
            title = child['id'].replace('-', ' ').capitalize().replace("Manga","Animación/Cine Oriental")
            title += " ([COLOR gold]"+str(child['number'])+"[/COLOR])"
            itemlist.append( Item(channel=__channel__, action='entradasconlistas', title=title , url=url , thumbnail=thumbnail, fanart=fanart, folder=True) )

    return itemlist

def entradas(item):
    logger.info("pelisalacarta.channels.tvvip entradas")
    itemlist = []
    if item.title == "Nuevos Capítulos": context = ""
    else: context = "0"
    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    for child in data["sortedRepoChilds"]:
        infolabels={}
        plot={}
        infolabels['plot'] = child['description']
        infolabels['year']= child['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',','.')
        infolabels['votes'] = child['rateCount']
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']: fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else: fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']: thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else: thumbnail = fanart
        thumbnail += head
        fanart += head
		
        if child['height'] < 720: quality = "[B]     [SD][/B]"
        elif child['height'] < 1080: quality = "[B]     [720p][/B]"
        elif child['height'] >= 1080: quality = "[B]     [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore').decode("utf-8")
        title = child['name']
        if child['year'] != "" : title += " (" + child['year'] + ")"
        title += quality
        if item.show != "": title = child['name']
        plot['infoLabels']=infolabels
        itemlist.append( Item(channel=__channel__, action='findvideos', server="", title=title , url=url , thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, plot=str(plot), contentTitle=fulltitle, context=context, viewmode="movie_with_plot", show=data['name'], folder=True) )

    return itemlist

def entradasconlistas(item):
    logger.info("pelisalacarta.channels.tvvip entradasconlistas")
    itemlist = []

    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    # Si hay alguna lista
    if data['playListChilds']:
        itemlist.append( Item(channel=__channel__, title="[COLOR red][B]**LISTAS**[/B][/COLOR]", fulltitle="**LISTAS**", folder=False) )
        for child in data['sortedPlaylistChilds']:
            infolabels={}
            plot={}
            infolabels['plot'] = "Contiene:\n"+"\n".join(child['playListChilds'])+"\n".join(child['repoChilds'])
            title = child['id'].replace('-', ' ').capitalize() + " ([COLOR gold]"+str(child['number'])+"[/COLOR])"
            url = "http://tv-vip.com/json/playlist/%s/index.json" % child["id"]
            thumbnail = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            if child['hashBackground']: fanart = "http://tv-vip.com/json/playlist/%s/background.jpg" % child["id"]
            else: fanart = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            plot['infoLabels']=infolabels
            thumbnail += head
            fanart += head
            itemlist.append( Item(channel=__channel__, action='entradasconlistas', title=title, url=url, thumbnail=thumbnail, fanart=fanart, fulltitle=child['id'], plot=str(plot), viewmode="movie_with_plot", folder=True) )
	    #itemlist.sort(key=lambda item: item.fulltitle)

    if data["sortedRepoChilds"] and len(itemlist) > 0:
        itemlist.append( Item(channel=__channel__, title="[COLOR blue][B]**VÍDEOS**[/B][/COLOR]", folder=False) )
        
    for child in data["sortedRepoChilds"]:
        infolabels={}
        plot={}
        infolabels['plot'] = child['description']
        infolabels['year']= data['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',','.')
        infolabels['votes'] = child['rateCount']
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']: fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else: fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']: thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else: thumbnail = fanart
        thumbnail += head
        fanart += head
        if child['height'] < 720: quality = "[B]     [SD][/B]"
        elif child['height'] < 1080: quality = "[B]     [720p][/B]"
        elif child['height'] >= 1080: quality = "[B]     [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore').decode("utf-8")
        if child['year']: title = child['name'] +  " (" + child['year'] + ")" + quality
        else: title = child['name'] +  quality
        plot['infoLabels'] = infolabels
        itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, plot=str(plot), contentTitle=fulltitle, context="0", viewmode="movie_with_plot", folder=True) )

    # Si no hay ninguna lista dentro, se añade item para añadirlo a la biblioteca
    if not data['playListChilds'] and len(itemlist) > 0:
        if config.get_library_support():
            itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir esta lista a la biblioteca[/COLOR]", url=item.url, action="listas"))

    return itemlist

def series(item):
    logger.info("pelisalacarta.channels.tvvip series")
    itemlist = []

    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    exception = ["top-series", "nuevos-capitulos"]
    for child in data["sortedPlaylistChilds"]:
        if child["id"] not in exception:
            infolabels={}
            plot={}
            infolabels['plot'] = child['description']
            infolabels['year']= child['year']
            if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
            infolabels['rating'] = child['rate'].replace(',','.')
            infolabels['votes'] = child['rateCount']
            if child['cast']: infolabels['cast'] = child['cast'].split(",")
            infolabels['director'] = child['director']
            infolabels['mediatype'] = "episode"
            if child['seasonNumber']: infolabels['season'] = child['seasonNumber']
            url = "http://tv-vip.com/json/playlist/%s/index.json" % child["id"]
            # Fanart
            if child['hashBackground']: fanart = "http://tv-vip.com/json/playlist/%s/background.jpg" % child["id"]
            else: fanart = "http://tv-vip.com/json/playlist/%s/thumbnail.jpg" % child["id"]
            # Thumbnail
            if child['hasPoster']: thumbnail = "http://tv-vip.com/json/playlist/%s/poster.jpg" % child["id"]
            else: thumbnail = fanart
            thumbnail += head
            fanart += head

            if item.contentTitle == "Series":
                fulltitle = unicodedata.normalize('NFD', unicode(child['name'].split(" Temporada")[0], 'utf-8')).encode('ASCII', 'ignore').decode("utf-8")
                fulltitle = fulltitle.replace('-','')
                title = child['name']+ " (" + child['year'] + ")"
                if "Temporada" not in title: title += "     [Temporadas: [COLOR gold]"+str(child['numberOfSeasons'])+"[/COLOR]]"
                elif item.title == "Más Vistas": title = title.replace("- Temporada","--- Temporada")
            else:
                fulltitle = unicodedata.normalize('NFD', unicode(data['name'], 'utf-8')).encode('ASCII', 'ignore').decode("utf-8")
                if child['seasonNumber']: title = data['name']+ " --- Temporada "+child['seasonNumber']+"  [COLOR gold]("+str(child['number'])+")[/COLOR]"
                else: title = child['name']+"  [COLOR gold]("+str(child['number'])+")[/COLOR]"
            plot['infoLabels']=infolabels
            if not child['playListChilds']: action = "episodios"
            else: action = "series"
            itemlist.append( Item(channel=__channel__, action=action, title=title, url=url, server="", thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, plot=str(plot), contentTitle=fulltitle, context="2", viewmode="movie_with_plot", folder=True) )
            if len(itemlist) == len(data["sortedPlaylistChilds"]) and item.contentTitle != "Series":
                itemlist.sort(key=lambda item: item.title, reverse=True)
                if config.get_library_support():
                    itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir esta serie a la biblioteca[/COLOR]", url=item.url, action="add_serie_to_library", extra="series_library", fulltitle=data['name'], show=data['name']))

    if item.title == "Últimas Series": return itemlist
    if item.title == "Lista de Series A-Z": itemlist.sort(key=lambda item: item.fulltitle)

    if data["sortedRepoChilds"] and len(itemlist) > 0:
        itemlist.append( Item(channel=__channel__, title="[COLOR blue][B]**VÍDEOS RELACIONADOS/MISMA TEMÁTICA**[/B][/COLOR]", folder=False) )
    for child in data["sortedRepoChilds"]:
        infolabels={}
        plot={}
        if child['description']: infolabels['plot'] = data['description']
        else: infolabels['plot'] = child['description']
        infolabels['year']= data['year']
        if not child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in data['tags']])
        else: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',','.')
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']

        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']: fanart = "http://tv-vip.com/json/repo/%s/background.jpg" % child["id"]
        else: fanart = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']: thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
        else: thumbnail = fanart
        thumbnail += head
        fanart += head
		
        if child['height'] < 720: quality = "[B]     [SD][/B]"
        elif child['height'] < 1080: quality = "[B]     [720p][/B]"
        elif child['height'] >= 1080: quality = "[B]     [1080p][/B]"
        fulltitle = unicodedata.normalize('NFD', unicode(child['name'], 'utf-8')).encode('ASCII', 'ignore').decode("utf-8")
        if child['year']: title = child['name'] +  " (" + child['year'] + ")" + quality
        else: title = child['name'] +  quality
        plot['infoLabels'] = infolabels
        itemlist.append( Item(channel=__channel__, action='findvideos', title=title , url=url , server="", thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, plot=str(plot), contentTitle=fulltitle, context="2", viewmode="movie_with_plot", folder=True) )
    if item.extra == "new":
        itemlist.sort(key=lambda item: item.title, reverse=True)

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.tvvip episodios")
    itemlist = []
    # Redirección para actualización de biblioteca
    if item.category != "":
        itemlist = series_library(item)
        return itemlist

    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    # Se prueba un método u otro porque algunas series no están bien listadas
    if data["sortedRepoChilds"]:
        for child in data["sortedRepoChilds"]:
            if item.plot != "": 
                item.plot = "{"+item.plot[1:-2]
                item.plot += ", 'duration': '"+str(child['duration'])+"'"
                item.plot += ", 'season': '"+str(data['seasonNumber'])+"'"
                item.plot += ", 'episode': '"+str(child['episode'])+"'"
                item.plot += ", 'mediatype': 'episode'}}"
            contentTitle = item.fulltitle+"|"+str(data['seasonNumber'])+"|"+str(child['episode'])
			# En caso de venir del apartado nuevos capítulos se redirige a la función series para mostrar los demás
            if item.title == "Nuevos Capítulos":
                url = "http://tv-vip.com/json/playlist/%s/index.json" % child["season"]
                action = "series"
                extra = "new"
            else:
                url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
                action = "findvideos"
                extra = ""
            if child['hasPoster']: thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child["id"]
            else: thumbnail = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child["id"]
            thumbnail += head
            title = fulltitle = child['name'].rsplit(" ",1)[0]+" - "+child['name'].rsplit(" ",1)[1]
            itemlist.append( Item(channel=__channel__, action=action, server="", title=title , url=url , thumbnail=thumbnail, fanart=item.fanart, fulltitle=fulltitle, plot=item.plot, contentTitle=contentTitle, context="3", viewmode="movie", extra=extra, show=item.fulltitle, folder=True) )
    else:
        for child in data["repoChilds"]:
            contentTitle = item.fulltitle
            url = "http://tv-vip.com/json/repo/%s/index.json" % child
            if data['hasPoster']: thumbnail = "http://tv-vip.com/json/repo/%s/poster.jpg" % child
            else: thumbnail = "http://tv-vip.com/json/repo/%s/thumbnail.jpg" % child
            thumbnail += head
            title = fulltitle = child.capitalize().replace('_',' ')
            itemlist.append( Item(channel=__channel__, action='findvideos', server="", title=title , url=url , thumbnail=thumbnail, fanart=item.fanart, fulltitle=fulltitle, plot=item.plot, contentTitle=contentTitle, context="2", viewmode="movie", show=item.fulltitle, folder=True) )

    # Opción de añadir a la biblioteca en casos de series de una única temporada
    if len(itemlist) > 0 and not "---" in item.title and item.title != "Nuevos Capítulos":
        if config.get_library_support() and item.show == "":
            show = item.title.split('-')[0]
            itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir esta serie a la biblioteca[/COLOR]", url=item.url, action="add_serie_to_library", extra="series_library", fulltitle=show, show=show))
    return itemlist

def series_library(item):
    logger.info("pelisalacarta.channels.tvvip series_library")
    # Funcion unicamente para añadir/actualizar series a la libreria
    itemlist = []
    show = item.show.strip()
  
    data_serie, cloudflare = anti_cloudflare(item.url)
    data_serie = jsontools.load_json(data_serie)
    # Para series que en la web se listan divididas por temporadas
    if data_serie["sortedPlaylistChilds"]:
        for season_name in data_serie["sortedPlaylistChilds"]:
            url_season = "http://tv-vip.com/json/playlist/%s/index.json" % season_name['id']
            data, cloudflare = anti_cloudflare(url_season)
            data = jsontools.load_json(data)

            if data["sortedRepoChilds"]:
                for child in data["sortedRepoChilds"]:
                    url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
                    fulltitle = child['name'].rsplit(" ",1)[0]+" - "+child['name'].rsplit(" ",1)[1]
                    itemlist.append( Item(channel=__channel__, action='findvideos', server="", title=url+"%"+fulltitle , url=item.url , fulltitle=fulltitle, show=show) )
            else:
                for child in data["repoChilds"]:
                    url = "http://tv-vip.com/json/repo/%s/index.json" % child
                    fulltitle = child.capitalize().replace('_',' ')
                    itemlist.append( Item(channel=__channel__, action='findvideos', server="", title=url+"&"+fulltitle , url=item.url , fulltitle=fulltitle, show=show) )
    # Para series directas de una sola temporada
    else:
        data = data_serie
        if data["sortedRepoChilds"]:
            for child in data["sortedRepoChilds"]:
                url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
                fulltitle = child['name'].rsplit(" ",1)[0]+" - "+child['name'].rsplit(" ",1)[1]
                itemlist.append( Item(channel=__channel__, action='findvideos', server="", title=url , url=item.url , fulltitle=fulltitle, show=show) )
        else:
            for child in data["repoChilds"]:
                url = "http://tv-vip.com/json/repo/%s/index.json" % child
                fulltitle = child.capitalize().replace('_',' ')
                itemlist.append( Item(channel=__channel__, action='findvideos', server="", title=url , url=item.url  , fulltitle=fulltitle, show=show) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.channels.tvvip findvideos")
    itemlist = []

    # En caso de llamarse a la función desde una serie de la biblioteca
    if item.title.startswith("http"): item.url = item.title.split('%')[0]
    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    if cloudflare: head = header_string + get_cookie_value()
    else: head = ""
    urls = []
    for child in data["profiles"].keys():
        videopath = urllib.quote(data["profiles"][child]['videoUri'])
        extension = videopath[-4:]
        for i in range(0, len(data["profiles"][child]['servers'])):
            url = data["profiles"][child]['servers'][i]['url'] + videopath + head
            urls.append(url)
            size = "  "+data["profiles"][child]["sizeHuman"]
            resolution = " ["+(data["profiles"][child]['videoResolution'])+"]"
            if i == 0: title = "Ver vídeo en " + resolution.replace('1920x1080','HD-1080p') + size + " [COLOR purple]Mirror "+str(i+1)+"[/COLOR]"
            else: title = "Ver vídeo en " + resolution.replace('1920x1080','HD-1080p') + size +  " [COLOR green]Mirror "+str(i+1)+"[/COLOR]"
            # Para poner enlaces de mayor calidad al comienzo de la lista
            if data["profiles"][child]["profileId"] == "default": itemlist.insert(i, Item(channel=__channel__, action='play', server='directo', title=title , url=url , thumbnail=item.thumbnail, fanart=item.fanart, fulltitle=item.fulltitle, plot=item.plot, folder=False) )
            else: itemlist.append( Item(channel=__channel__, action='play', server='directo', title=title , url=url , thumbnail=item.thumbnail, fanart=item.fanart, fulltitle=item.fulltitle, plot=item.plot, folder=False) )
    for transcoder in data["transcoders"]:
        if transcoder == "hn": continue
        if cloudflare: head = header_string + get_cookie_value(data['id'][-4:])
        else: head = ""
        id = urllib.quote(data['id'])
        url_default = "http://"+transcoder+".tv-vip.com/transcoder/"+id+"/default/"+id+head
        title = "Ver vídeo en  ["+data["videoResolution"].replace('1920x1080','HD-1080p')+"] "+data["sizeHuman"]
        if not url_default in urls: itemlist.insert(0, Item(channel=__channel__, action='play', server='directo', title=title , url=url_default , thumbnail=item.thumbnail, fanart=item.fanart, fulltitle=item.fulltitle, plot=item.plot, folder=False) )
    if len(itemlist) > 0 and item.category == "":
        if config.get_library_support():
            itemlist.append( Item(channel=__channel__, title="[COLOR green]Añadir enlaces a la biblioteca[/COLOR]", url=item.url, action="add_pelicula_to_library", fulltitle=item.fulltitle))
 
    return itemlist

def listas(item):
    logger.info("pelisalacarta.channels.tvvip listas")
    # Para añadir listas a la biblioteca en carpeta CINE
    itemlist = []
    data, cloudflare = anti_cloudflare(item.url)
    data = jsontools.load_json(data)
    for child in data["sortedRepoChilds"]:
        url = "http://tv-vip.com/json/repo/%s/index.json" % child["id"]
        title = scrapertools.slugify(child['name'])
        title = title.replace('-',' ').capitalize()
        try:
            from platformcode import library
            library.savelibrary(titulo=title, url=url, server='', canal="tvvip", category="Cine")
            error = False
        except:
            error = True
            pass

    if not error:
        itemlist.append(Item(title = 'Lista añadida correctamente a la biblioteca'))
    else:
        itemlist.append(Item(title = 'ERROR. Han ocurrido uno o varios errores en el proceso'))

    return itemlist

def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        scrapertools.get_headers_from_response(host + '/' + resp_headers['refresh'][7:], headers=headers)

    try:
        data = scrapertools.downloadpageGzip(url)
        cloudflare = False
    except:
        data = scrapertools.cache_page(url, headers=headers)
        cloudflare = True

    return data, cloudflare

def get_cookie_value(extension=""):
    cookies = os.path.join( config.get_data_path(), 'cookies.dat' )
    cookiedatafile = open(cookies,'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close();
    cfduid = scrapertools.find_single_match(cookiedata,"tv-vip.*?__cfduid\s+([A-Za-z0-9\+\=]+)")
    cf_clearance = scrapertools.find_single_match(cookiedata,"tv-vip.*?cf_clearance\s+([A-Za-z0-9\+\=-]+)")
    cookie = "&Cookie=__cfduid="+cfduid+extension+"; cf_clearance="+cf_clearance
    return cookie
