# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import os

from core import config
from core import logger
from core.item import Item
from core import channeltools

__channel__ = "buscador"

logger.info("pelisalacarta.channels.buscador init")

DEBUG = True


def isGeneric():
    return True


def mainlist(item,preferred_thumbnail="squares"):
    logger.info("pelisalacarta.channels.buscador mainlist")

    itemlist = list()
    itemlist.append(Item(channel=__channel__, action="search", title="Realizar nueva búsqueda..."))

    saved_searches_list = get_saved_searches()

    for saved_search_text in saved_searches_list:
        itemlist.append(Item(channel=__channel__, action="do_search", title=' "'+saved_search_text+'"',
                             extra=saved_search_text))

    if len(saved_searches_list) > 0:
        itemlist.append(Item(channel=__channel__, action="clear_saved_searches", title="Borrar búsquedas guardadas"))

    return itemlist


# Al llamar a esta función, el sistema pedirá primero el texto a buscar
# y lo pasará en el parámetro "tecleado"
def search(item, tecleado):
    logger.info("pelisalacarta.channels.buscador search")

    if tecleado != "":
        save_search(tecleado)

    item.extra = tecleado
    return do_search(item)


# Esta es la función que realmente realiza la búsqueda
def do_search(item):
    logger.info("pelisalacarta.channels.buscador do_search")

    tecleado = item.extra

    itemlist = []

    import os
    import glob
    import imp

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("pelisalacarta.channels.buscador channels_path="+channels_path)

    channel_language = config.get_setting("channel_language")
    logger.info("pelisalacarta.channels.buscador channel_language="+channel_language)
    if channel_language == "":
        channel_language = "all"
        logger.info("pelisalacarta.channels.buscador channel_language="+channel_language)

    show_dialog = False
    progreso = None
    if config.is_xbmc():
        show_dialog = True

    try:
        import xbmcgui
        progreso = xbmcgui.DialogProgressBG()
        progreso.create("Buscando " + tecleado.title())
    except ImportError:
        xbmcgui = None
        show_dialog = False

    channel_files = glob.glob(channels_path)
    number_of_channels = len(channel_files)

    for index, infile in enumerate(channel_files):
        percentage = index*100/number_of_channels

        basename = os.path.basename(infile)
        basename_without_extension = basename[:-4]

        channel_parameters = channeltools.get_channel_parameters(basename_without_extension)

        # No busca si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # No busca si es un canal excluido de la busqueda global
        if channel_parameters["include_in_global_search"] != "true":
            continue

        # No busca si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No busca si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        if show_dialog:
            progreso.update(percentage, ' Buscando "' + tecleado + '"', basename_without_extension)

        logger.info("pelisalacarta.channels.buscador Intentado busqueda en " + basename_without_extension + " de " +
                    tecleado)
        try:

            # http://docs.python.org/library/imp.html?highlight=imp#module-imp
            obj = imp.load_source(basename_without_extension, infile[:-4]+".py")
            logger.info("pelisalacarta.channels.buscador cargado " + basename_without_extension + " de " + infile)
            channel_result_itemlist = obj.search(Item(), tecleado)
            for item in channel_result_itemlist:
                item.title = item.title + "[" + basename_without_extension + "]"
                item.viewmode = "list"

            itemlist.extend(channel_result_itemlist)
        except:
            import traceback
            logger.error(traceback.format_exc())

    itemlist = sorted(itemlist, key=lambda Item: Item.title) 

    if show_dialog:
        progreso.close()

    return itemlist


def save_search(text):

    saved_searches_limit = (10, 20, 30, 40, )[int(config.get_setting("saved_searches_limit"))]

    if os.path.exists(os.path.join(config.get_data_path(), "saved_searches.txt")):
        f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "r")
        saved_searches_list = f.readlines()
        f.close()
    else:
        saved_searches_list = []

    saved_searches_list.append(text)

    if len(saved_searches_list) >= saved_searches_limit:
        # Corta la lista por el principio, eliminando los más recientes
        saved_searches_list = saved_searches_list[-saved_searches_limit:]

    f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "w")
    for saved_search in saved_searches_list:
        f.write(saved_search+"\n")
    f.close()


def clear_saved_searches(item):

    f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "w")
    f.write("")
    f.close()


def get_saved_searches():

    if os.path.exists(os.path.join(config.get_data_path(), "saved_searches.txt")):
        f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "r")
        saved_searches_list = f.readlines()
        f.close()
    else:
        saved_searches_list = []

    # Invierte la lista, para que el último buscado salga el primero
    saved_searches_list.reverse()

    trimmed = []
    for saved_search_text in saved_searches_list:
        trimmed.append(saved_search_text.strip())
    
    return trimmed
