# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse
import os
import sys
import traceback
import glob

from core import config
from core import logger
from core.item import Item
from core import channeltools

DEBUG = True
CHANNELNAME = "channelselector"

def getmainlist(preferred_thumb=""):
    logger.info("channelselector.getmainlist")
    itemlist = []

    # Añade los canales que forman el menú principal
    itemlist.append( Item(title=config.get_localized_string(30130) , channel="novedades" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_novedades.png"),viewmode="movie") )
    itemlist.append( Item(title=config.get_localized_string(30118) , channel="channelselector" , action="channeltypes", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales.png"),viewmode="movie") )
    itemlist.append( Item(title=config.get_localized_string(30103) , channel="buscador" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_buscar.png"),viewmode="movie") )
    itemlist.append( Item(title=config.get_localized_string(30102) , channel="favoritos" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_favoritos.png"),viewmode="movie") )
    itemlist.append( Item(title=config.get_localized_string(30131) , channel="wiideoteca" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_biblioteca.png"),viewmode="movie") )
    itemlist.append( Item(title=config.get_localized_string(30101) , channel="descargas" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_descargas.png"),viewmode="movie") )

    if "xbmceden" in config.get_platform():
        itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_configuracion.png"), folder=False,viewmode="movie") )
    else:
        itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_configuracion.png"),viewmode="movie") )

    itemlist.append( Item(title=config.get_localized_string(30104) , channel="ayuda" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_ayuda.png"),viewmode="movie") )
    return itemlist

# TODO: (3.1) Pasar el código específico de XBMC al laucher
def mainlist(params,url,category):
    logger.info("channelselector.mainlist")

    # Verifica actualizaciones solo en el primer nivel
    if config.get_platform()!="boxee":

        try:
            from core import updater
        except ImportError:
            logger.info("channelselector.mainlist No disponible modulo actualizaciones")
        else:
            if config.get_setting("updatecheck2") == "true":
                logger.info("channelselector.mainlist Verificar actualizaciones activado")
                try:
                    updater.checkforupdates()
                except:
                    import xbmcgui
                    dialog = xbmcgui.Dialog()
                    dialog.ok("No se puede conectar","No ha sido posible comprobar","si hay actualizaciones")
                    logger.info("channelselector.mainlist Fallo al verificar la actualización")
                    pass
            else:
                logger.info("channelselector.mainlist Verificar actualizaciones desactivado")

    itemlist = getmainlist()
	#Se devuelve el itemlist para que xbmctools se encarge de mostrarlo
    return itemlist

def getchanneltypes(preferred_thumb=""):
    logger.info("channelselector getchanneltypes")

    # Lista de categorias
    valid_types = [ "movie","serie","anime","documentary","vos","torrent","latino","adult"]

    # Lee la lista de canales
    channel_path = os.path.join( config.get_runtime_path() , "channels" , '*.xml' )
    logger.info("channelselector.getchanneltypes channel_path="+channel_path)

    channel_files = glob.glob(channel_path)

    channel_language = config.get_setting("channel_language")
    logger.info("channelselector.getchanneltypes channel_language="+channel_language)

    # Construye la lista de tipos
    channel_types = []

    for index, channel in enumerate(channel_files):
        logger.info("channelselector.getchanneltypes channel="+channel)
        if channel.endswith(".xml"):
            try:
                channel_parameters = channeltools.get_channel_parameters(channel[:-4])
                logger.info("channelselector.filterchannels channel_parameters="+repr(channel_parameters))

                # Si es un canal para adultos y el modo adulto está desactivado, se lo salta
                if channel_parameters["adult"]=="true" and config.get_setting("adult_mode")=="false":
                    continue

                # Si el canal está en un idioma filtrado
                if channel_language!="all" and channel_parameters["language"]!=channel_language:
                    continue

                categories = channel_parameters["categories"]
                for category in categories:
                    logger.info("channelselector.filterchannels category="+category)
                    if category not in channel_types and category in valid_types:
                        channel_types.append(category)

            except:
                logger.info("Se ha producido un error al leer los datos del canal " + channel + traceback.format_exc())

    logger.info("channelselector.getchanneltypes Encontrados:")
    for channel_type in channel_types:
        logger.info("channelselector.getchanneltypes channel_type="+channel_type)

    # Ahora construye el itemlist ordenadamente
    itemlist = []

    dict_cat_lang = {'movie': config.get_localized_string(30122), 'serie': config.get_localized_string(30123),
                     'anime': config.get_localized_string(30124), 'documentary': config.get_localized_string(30125),
                     'vos': config.get_localized_string(30136), 'adult': config.get_localized_string(30126),
                     'latino': config.get_localized_string(30127)}

    itemlist.append(Item(title=config.get_localized_string(30121), channel="channelselector", action="listchannels",
                         category="all", thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),
                                                                    "thumb_canales_todos.png"),viewmode="movie"))
    logger.info("channelselector.getchanneltypes Ordenados:")
    for channel_type in valid_types:
        logger.info("channelselector.getchanneltypes channel_type="+channel_type)
        if channel_type in channel_types:
            title = channel_type
            if channel_type in dict_cat_lang:
                title = dict_cat_lang[channel_type]

            itemlist.append(Item(title=title, channel="channelselector", action="listchannels", category=channel_type,
                                 thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),
                                                            "thumb_canales_"+channel_type+".png"),viewmode="movie"))

    return itemlist

def channeltypes(params,url,category):
    logger.info("channelselector.mainlist channeltypes")

    lista = getchanneltypes()
	#Se devuelve el itemlist para que xbmctools se encarge de mostrarlo
    return lista

def listchannels(params,url,category):
    logger.info("channelselector.listchannels")

    lista = filterchannels(category)
	#Se devuelve el itemlist para que xbmctools se encarge de mostrarlo
    return lista

def filterchannels(category,preferred_thumb=""):
    logger.info("channelselector.filterchannels")

    channelslist =[]

    # Lee la lista de canales
    channel_path = os.path.join( config.get_runtime_path() , "channels" , '*.xml' )
    logger.info("channelselector.filterchannels channel_path="+channel_path)

    channel_files = glob.glob(channel_path)
    logger.info("channelselector.filterchannels channel_files encontrados "+str(len(channel_files)))

    channel_language = config.get_setting("channel_language")
    logger.info("channelselector.filterchannels channel_language="+channel_language)
    if channel_language=="":
        channel_language = "all"
        logger.info("channelselector.filterchannels channel_language="+channel_language)

    for index, channel in enumerate(channel_files):
        logger.info("channelselector.filterchannels channel="+channel)
        if channel.endswith(".xml"):

            try:
                channel_parameters = channeltools.get_channel_parameters(channel[:-4])
                logger.info("channelselector.filterchannels channel_parameters="+repr(channel_parameters))

                # Si prefiere el bannermenu y el canal lo tiene, cambia ahora de idea
                if preferred_thumb=="bannermenu" and "bannermenu" in channel_parameters:
                    channel_parameters["thumbnail"] = channel_parameters["bannermenu"]

                # Se salta el canal si no está activo
                if not channel_parameters["active"] == "true":
                    continue

                # Se salta el canal para adultos si el modo adultos está desactivado
                if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") != "true": 
                    continue

                # Se salta el canal si está en un idioma filtrado
                if channel_language!="all" and channel_parameters["language"]!=config.get_setting("channel_language"):
                    continue

                # Se salta el canal si está en una categoria filtrado
                if category!="all" and category not in channel_parameters["categories"]:
                    continue

                # Si ha llegado hasta aquí, lo añade
                channelslist.append(Item(title=channel_parameters["title"], channel=channel_parameters["channel"], action="mainlist", thumbnail=channel_parameters["thumbnail"] , fanart=channel_parameters["fanart"], category=", ".join(channel_parameters["categories"])[:-2], language=channel_parameters["language"], type=channel_parameters["type"], viewmode="movie" ))
            
            except:
                logger.info("Se ha producido un error al leer los datos del canal " + channel)
                import traceback
                logger.info(traceback.format_exc())
           
    channelslist.sort(key=lambda item: item.title.lower().strip())

    if category=="all":
        if config.get_setting("personalchannel5")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname5") ,action="mainlist", channel="personal5" ,thumbnail=config.get_setting("personalchannellogo5") , type="generic" ,viewmode="movie" ))
        if config.get_setting("personalchannel4")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname4") ,action="mainlist", channel="personal4" ,thumbnail=config.get_setting("personalchannellogo4") , type="generic" ,viewmode="movie" ))
        if config.get_setting("personalchannel3")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname3") ,action="mainlist", channel="personal3" ,thumbnail=config.get_setting("personalchannellogo3") , type="generic" ,viewmode="movie" ))
        if config.get_setting("personalchannel2")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname2") ,action="mainlist", channel="personal2" ,thumbnail=config.get_setting("personalchannellogo2") , type="generic" ,viewmode="movie" ))
        if config.get_setting("personalchannel")=="true":
            channelslist.insert( 0 , Item( title=config.get_setting("personalchannelname")  ,action="mainlist", channel="personal"  ,thumbnail=config.get_setting("personalchannellogo") , type="generic" ,viewmode="movie" ))

        channel_parameters = channeltools.get_channel_parameters("tengourl")
        # Si prefiere el bannermenu y el canal lo tiene, cambia ahora de idea
        if preferred_thumb=="bannermenu" and "bannermenu" in channel_parameters:
            channel_parameters["thumbnail"] = channel_parameters["bannermenu"]

        channelslist.insert( 0 , Item( title="Tengo una URL"  ,action="mainlist", channel="tengourl" , thumbnail=channel_parameters["thumbnail"], type="generic" ,viewmode="movie" ))

    return channelslist

def get_thumbnail_path(preferred_thumb=""):

    WEB_PATH = ""
    
    if preferred_thumb=="":
        thumbnail_type = config.get_setting("thumbnail_type")
        if thumbnail_type=="":
            thumbnail_type="2"

        if thumbnail_type=="0":
            WEB_PATH = "http://media.tvalacarta.info/pelisalacarta/posters/"
        elif thumbnail_type=="1":
            WEB_PATH = "http://media.tvalacarta.info/pelisalacarta/banners/"
        elif thumbnail_type=="2":
            WEB_PATH = "http://media.tvalacarta.info/pelisalacarta/squares/"
    else:
        WEB_PATH = "http://media.tvalacarta.info/pelisalacarta/"+preferred_thumb+"/"

    return WEB_PATH
