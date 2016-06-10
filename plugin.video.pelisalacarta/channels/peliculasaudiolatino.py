# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para peliculasaudiolatino
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "peliculasaudiolatino"
__category__ = "F"
__type__ = "generic"
__title__ = "Peliculasaudiolatino"
__language__ = "ES"
__creationdate__ = "20111014"

DEBUG = config.get_setting("debug")
    
def isGeneric():
    return True

def mainlist(item):
    logger.info("channels.peliculasaudiolatino mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Recién agregadas", action="peliculas", url="http://peliculasaudiolatino.com/ultimas-agregadas.html"))
    itemlist.append( Item(channel=__channel__, title="Recién actualizadas", action="peliculas", url="http://peliculasaudiolatino.com/recien-actualizadas.html"))
    itemlist.append( Item(channel=__channel__, title="Las más vistas", action="peliculas", url="http://peliculasaudiolatino.com/las-mas-vistas.html"))
    
    itemlist.append( Item(channel=__channel__, title="Listado por géneros" , action="generos", url="http://peliculasaudiolatino.com"))
    itemlist.append( Item(channel=__channel__, title="Listado por años" , action="anyos", url="http://peliculasaudiolatino.com"))
    
    itemlist.append( Item(channel=__channel__, title="Buscar..." , action="search") )
    return itemlist

def peliculas(item):
    logger.info("channels.peliculasaudiolatino peliculas")

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Extrae las entradas de la pagina seleccionada
    patron  = '<div class="top"[^<]+'
    patron += '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)">'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""

        # Añade al listado
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , fulltitle=title, url=url , thumbnail=thumbnail , plot=plot , viewmode="movie", folder=True) )

    # Extrae la marca de siguiente página
    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)"><span class="icon-chevron-right">')
    if next_page!="":
        itemlist.append( Item(channel=__channel__, action="peliculas", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page).replace("/../../","/"), folder=True) )

    return itemlist

def generos(item):
    logger.info("channels.peliculasaudiolatino generos")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Limita el bloque donde buscar
    data = scrapertools.find_single_match(data,'span>Generos<span(.*?)</ul>')

    # Extrae las entradas
    patron = '<li><a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if (DEBUG): scrapertools.printMatches(matches)
                                          
    for match in matches:
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedtitle = match[1].strip()
        scrapedthumbnail = ""
        scrapedplot = ""
        logger.info(scrapedtitle)

        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    itemlist = sorted(itemlist, key=lambda Item: Item.title)    
    return itemlist
    
def anyos(item):
    logger.info("channels.peliculasaudiolatino anyos")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Limita el bloque donde buscar
    data = scrapertools.find_single_match(data,"span>Ultimo A(.*?)</ul>")
    logger.info("channels.peliculasaudiolatino data="+data)

    # Extrae las entradas
    patron = '<li><a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if (DEBUG): scrapertools.printMatches(matches)
                                          
    for scrapedurl,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="peliculas", title=title , url=url , thumbnail=thumbnail , plot=plot, folder=True) )

    return itemlist

def search(item,texto):
    logger.info("channels.peliculasaudiolatino search")
    itemlist = []

    texto = texto.replace(" ","+")
    try:
        # Series
        item.url="http://peliculasaudiolatino.com/busqueda.php?q=%s"
        item.url = item.url % texto
        item.extra = ""
        itemlist.extend(peliculas(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 
        
        return itemlist
        
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def findvideos(item):
    logger.info("channels.peliculasaudiolatino videos")
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    title = item.title
    scrapedthumbnail = item.thumbnail
    itemlist = []
    '''
    <tr>
    <th class="headtable" align="left"><a href="http://peliculasaudiolatino.com/perfil/KAOSNORMAL.html" target="_blank"><img class="smallpic" src="http://peliculasaudiolatino.com/userpic/userpic1457229143.jpg" height="20" width="20">KAOSNORMAL</a></th>
    <th class="headmovil" align="left"><img src="http://www.google.com/s2/favicons?domain=gamovideo.com" width="16"/>gamovideo.com</th>
    <th class="headmovil" align="left"><img src="http://peliculasaudiolatino.com/images/la_la.png" width="22" align=absmiddle></th>
    <th class="headtable" align="left"><img src="http://peliculasaudiolatino.com/images/1dvd.png"> DVD</th>
    <th class="slink" align="left"><div id="btnp"><a href="javascript:void(0);" style="cursor:pointer" onClick="window.open('http://peliculasaudiolatino.com/movies/Samba/141400.html','mywindow','width=1000,height=800,location=no,status=no,scrollbars=yes,toolbar=no,menubar=no,directories=no');"><span class="headmovil">Ver</span></a></div> </th>
    </tr>
    '''
    '''
    <tr>
    <th class="headtable" align="left"><a href="http://peliculasaudiolatino.com/perfil/KAOSNORMAL.html" target="_blank"><img class="smallpic" src="http://peliculasaudiolatino.com/userpic/userpic1457229143.jpg" height="20" width="20">KAOSNORMAL</a></th>
    <th class="headmovil" align="left"><img src="http://www.google.com/s2/favicons?domain=userscloud.com" width="16"/>userscloud.com</th>
    <th class="headmovil" align="left"><img src="http://peliculasaudiolatino.com/images/la_la.png" width="22" align=absmiddle></th>
    <th class="headtable" align="left"><img src="http://peliculasaudiolatino.com/images/1dvd.png"> DVD</th>
    <th class="slink" align="left"><div id="btnp"><a href="http://peliculasaudiolatino.com/externo.php?host=http://www.userscloud.com/rid15pn653zu" target="_blank"><span class="headmovil">Descargar</span></a></div> </th>
    </tr>
    '''
    patron  = '<th class="headtable" align="left">.*?</th[^<]+'
    patron += '<th class="headmovil" align="left"><img[^>]+>([^<]+)</th[^<]+'
    patron += '<th class="headmovil" align="left"><img src="([^"]+)"[^<]+</th[^<]+'
    patron += '<th class="headtable" align="left"><img[^>]+>([^<]+)</th>'
    patron += '<th class="slink" align="left"><div id="btnp"><a href="(.*?)<span class="headmovil">Ver</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if (DEBUG): scrapertools.printMatches(matches)
    for servidor,imgidioma,calidad,scrapedurl in matches:
        url = scrapedurl
        idioma = img_idioma_to_img_name(imgidioma)
        title = "Ver en "+servidor+" ["+idioma+"]["+calidad+"]"
        itemlist.append( Item(channel=__channel__, action="play", title=title , fulltitle=item.fulltitle, url=url , thumbnail=scrapedthumbnail , folder=False) )

    return itemlist

def img_idioma_to_img_name(imgidioma):

    if "la_la.png" in imgidioma:
        return "Latino"
    elif "es_es" in imgidioma:
        return "Español"
    elif "en_es" in imgidioma:
        return "Subtitulado"
    else:
        return scrapertools.get_filename_from_url(imgidioma)

def play(item):
    logger.info("channels.peliculasaudiolatino play")
    itemlist=[]

    data2 = item.url

    if data2.startswith("javascript"):

        item.url = scrapertools.find_single_match(data2,"window.open\('([^']+)'")
        data2 = scrapertools.cache_page(item.url)
    
    logger.info("data2="+data2)
    data2 = data2.replace("http://peliculasaudiolatino.com/show/vidbux.php?url=","http://www.vidbux.com/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/vidxden.php?url=","http://www.vidxden.com/")

    data2 = data2.replace("http://peliculasaudiolatino.com/v/pl/play.php?url=","http://www.putlocker.com/embed/")
    data2 = data2.replace("http://peliculasaudiolatino.com/v/mv/play.php?url=","http://www.modovideo.com/frame.php?v=")
    data2 = data2.replace("http://peliculasaudiolatino.com/v/ss/play.php?url=","http://www.sockshare.com/embed/")
    data2 = data2.replace("http://peliculasaudiolatino.com/v/vb/play.php?url=","http://vidbull.com/")
    data2 = data2.replace("http://peliculasaudiolatino.com/v/vk/play.php?url=","http://vk.com/video_ext.php?oid=")
    data2 = data2.replace("http://peliculasaudiolatino.com/v/ttv/play.php?url=","http://www.tumi.tv/")

    data2 = data2.replace("http://peliculasaudiolatino.com/show/sockshare.php?url=","http://www.sockshare.com/embed/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/moevide.php?url=","http://moevideo.net/?page=video&uid=")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/novamov.php?url=","http://www.novamov.com/video/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/movshare.php?url=","http://www.movshare.net/video/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/divxstage.php?url=","http://www.divxstage.net/video/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/tumi.php?url=","http://www.tumi.tv/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/playerto.php?url=","http://played.to/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/videoweed.php?url=","http://www.videoweed.es/file/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/netu.php?url=","http://netu.tv/watch_video.php?v=")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/powvideo.php?url=","http://powvideo.net/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/streamin.php?url=","http://streamin.to/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/vidspot.php?url=","http://vidspot.net/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/allmy.php?url=","http://allmyvideos.net/")
    data2 = data2.replace('http://peliculasaudiolatino.com/show/r"></iframe>url=',"http://realvid.net/")

    data2 = data2.replace("http://peliculasaudiolatino.com/show/roc.php?url=","http://rocvideo.net/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/vide.php?url=","http://thevideo.me/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/vidto.php?url=","http://vidto.me/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/vodlocker.php?url=","http://vodlocker.com/")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/videomega.php?url=","http://videomega.tv/?ref=")
    data2 = data2.replace("http://peliculasaudiolatino.com/show/gamo.php?url=","http://gamovideo.com/")
    data2 = data2.replace("%26","&")
    logger.info("data2="+data2)

    listavideos = servertools.findvideos(data2)
    for video in listavideos:
        scrapedtitle = item.title+video[0]
        videourl = video[1]
        server = video[2]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+videourl+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle , fulltitle=item.fulltitle, url=videourl , server=server , folder=False) )
    
    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    novedades_items = peliculas(mainlist_items[0])
    bien = False
    for novedades_item in novedades_items:
        mirrors = findvideos( item=novedades_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien