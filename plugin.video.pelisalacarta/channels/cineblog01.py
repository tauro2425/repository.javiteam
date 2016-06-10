# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cineblog01
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import re, htmlentitydefs

from core import scrapertools
from core import logger
from core import config
from core.item import Item

__channel__ = "cineblog01"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "Cineblog01 (IT)"
__language__ = "IT"
sito="http://www.cb01.eu/"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []
	

    # Main options
    itemlist.append( Item(channel=__channel__, action="peliculas"  , title="Film - Novita'" , url=sito))
    itemlist.append( Item(channel=__channel__, action="menugeneros", title="Film - Per genere" , url=sito))
    itemlist.append( Item(channel=__channel__, action="menuanyos"  , title="Film - Per anno" , url=sito))
    itemlist.append( Item(channel=__channel__, action="search"     , title="Film - Cerca" ))
    itemlist.append( Item(channel=__channel__, action="peliculas"  , title="Serie Tv" , url=sito+"/serietv/" ))
    itemlist.append( Item(channel=__channel__, action="search", title="Serie Tv - Cerca" , extra="serie"))
    itemlist.append( Item(channel=__channel__, action="peliculas"  , title="Anime" , url="http://www.cineblog01.cc/anime/" ))

    return itemlist

def menugeneros(item):
    logger.info("[cineblog01.py] menuvk")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select2"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def menuanyos(item):
    logger.info("[cineblog01.py] menuvk")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)
    
    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select3"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto):
    logger.info("[cineblog01.py] "+item.url+" search "+texto)

    try:

        if item.extra=="serie":
            item.url = "http://www.cb01.org/serietv/?s="+texto
            return listserie(item)
        else:
            item.url = "http://www.cb01.org/?s="+texto
            return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url =="":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    if DEBUG: logger.info(data)

    # Extrae las entradas (carpetas)
    '''
    <div class="span4"> <a href="http://www.cb01.eu/testament-of-youth-sub-ita-2014/"><p><img src="http://www.locandinebest.net/imgk/testament_of_youth.jpg"></p>
    </a>
    <!--<img src="http://www.cb01.eu/wp-content/themes/cb01-new_2015/images/film-img1.png"  alt=""/>-->
    </div>
    <div class="span8">
    <!--<div class="index_post_content">-->
    <a href="http://www.cb01.eu/testament-of-youth-sub-ita-2014/"> <h1>Testament of Youth [Sub-ITA] (2014)</h1></a>
    <!--<p>COMEDY - DURATION 92 '- USA<br>-->
    <p><strong>BIOGRAFICO &#8211; DURATA 132&#8242; &#8211; USA</strong>                                <br />
    L&#8217;incontenibile e intelligente Vera Brittain sfida i pregiudizi della famiglia e della città natale per ottenere una borsa di studio a Oxford. Mentre persegue i suoi sogni letterari, Vera si innamora di Roland Leighton, il migliore amico del fratello&#8230;
    +Info &raquo;
    ...
    <div class="rating">
    '''
    '''
    <div class="span4"> <a href="http://www.cb01.eu/serietv/under-the-dome/"><p><img src="http://www.locandinebest.net/imgk/under_the_dome.jpg" alt="" width="350" height="" /></p>
    </a>
    <!--<img src="http://www.cb01.eu/serietv/wp-content/themes/cb01-new_2015/images/film-img1.png"  alt=""/>-->
    </div>
    <div class="span8">
    <!--<div class="index_post_content">-->
    <a href="http://www.cb01.eu/serietv/under-the-dome/"> <h1>Under the Dome</h1></a>
    <!--<p>COMEDY - DURATION 92 '- USA<br>-->



    FANTASCIENZA / MISTERO / DRAMMATICO (2013-)
    È una tiepida mattina d&#8217;autunno a Chester&#8217;s Mill, nel Maine, una mattina come tante altre. All&#8217;improvviso, una specie di cilindro trasparente cala sulla cittadina, tranciando in due tutto quello che si trova lungo il suo perimetro: cose, animali, persone. Come se dal cielo fosse scesa l                                <br><a href="http://www.cb01.eu/serietv/under-the-dome/">+ info » ...</a><br><br>
    <!--</div>-->
    <!--<div class="info">-->
    <div class="rating"> 
    '''
    patronvideos  = '<div class="span4"[^<]+'
    patronvideos += '<a href="([^"]+)"><p><img src="([^"]+)"[^<]+</p[^<]+'
    patronvideos += '</a[^<]+'
    patronvideos += '<!--<img[^>]+>--[^<]+'
    patronvideos += '</div[^<]+'
    patronvideos += '<div class="span8"[^<]+'
    patronvideos += '<!--<div class="index_post_content">--[^<]+'
    patronvideos += '<a[^<]+<h1>([^<]+)</h1></a>(.*?)<div class="rating">'

    #patronvideos += '<div id="description"><p>(.?*)</div>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, viewmode="movie_with_plot", fanart=thumbnail))

    # Next page mark
    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)">></a></li>')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="peliculas" , title=">> Next page" , url=next_page_url))

    return itemlist

def listserie(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    if DEBUG: logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos  = '<div id="covershot"><a[^<]+<p[^<]+<img.*?src="([^"]+)".*?'
    patronvideos += '<div id="post-title"><a href="([^"]+)"><h3>([^<]+)</h3></a></div>[^<]+'
    patronvideos += '<div id="description"><p>(.*?)</p>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedplot = scrapertools.unescape(match[3])
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data,"<link rel='next' href='([^']+)'")
        itemlist.append( Item(channel=__channel__, action="listserie" , title=">> Next page" , url=next_page, thumbnail=scrapedthumbnail, plot=scrapedplot))
    except:
        pass

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Comprueba que todas las opciones por categorias tengan algo (excepto los buscadores)
    for mainlist_item in mainlist_items:
        if mainlist_item.action.startswith("menu"):
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
            
            # Lee la primera categoría sólo
            exec "itemlist2 ="+itemlist[0].action+"(itemlist[0])"
            if len(itemlist2)==0:
                return false

    # Comprueba si alguno de los vídeos de "Novedades" devuelve mirrors
    for mainlist_item in mainlist_items:
        if mainlist_item.action=="peliculas" or mainlist_item.action=="listserie":
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
    
            bien = False
            for episodio_item in itemlist:
                from servers import servertools
                mirrors = servertools.find_video_items(item=episodio_item)
                if len(mirrors)>0:
                    bien = True
                    break

    return bien
