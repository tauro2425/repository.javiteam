# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cinetux
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
import time

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "cinetux"
__category__ = "F"
__type__ = "generic"
__title__ = "Cinetux"
__language__ = "ES"

host = "http://www.cinetux.org/"

headers = [
    ["User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"],
    ["Accept-Encoding", "gzip, deflate"],
    ["Referer", host]
]

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cinetux.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="peliculas", title="Destacadas o actualizadas" , url="http://www.cinetux.org/destacados", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="peliculas", title="Novedades" , url="http://www.cinetux.org/", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="bloque", title="Novedades subtitulado" , url="http://www.adsctx.net/sub.html", extra="Nuevo Sub", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="bloque", title="Novedades DVD" , url="http://www.adsctx.net/dvdrip.html", extra="ltimo DVDRIP", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="bloque", title="Novedades latino" , url="http://www.adsctx.net/latino.html", extra="Nuevo Latino", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="bloque", title="Novedades castellano" , url="http://www.adsctx.net/castellano.html", extra="Nuevo Castellano", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="bloque", title="Nueva calidad disponible" , url="http://www.adsctx.net/calidad.html", extra="Nueva Calidad", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="generos", title="Por géneros" , url="http://www.cinetux.org/", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" ))
    itemlist.append( Item(channel=__channel__ , action="search"        , title="Buscar"              , url="http://www.cinetux.org/?s=" ))

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

    return scrapertools.cache_page(url, headers=headers)

def search(item,texto):
    logger.info("[cinetux.py] search")
    if item.url=="":
        item.url="http://www.cinetux.org/?s="
    texto = texto.replace(" ","+")
    item.url = item.url+texto
    try:
        return busqueda(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []
        
def busqueda(item):
    logger.info("[cinetux.py] bloque")
    itemlist = []

    # Descarga la página
    data = anti_cloudflare(item.url)
    #data = scrapertools.get_match(data,item.extra+'</h6>(.*?)</div>')
    
    #<a target="_blank" href="http://www.cinetux.org/2013/04/ver-pelicula-dark-skies-online-gratis-2013.html"><img style="border:1px solid #FDC101;" src="http://4.bp.blogspot.com/-UlKHsLS3Tsk/URJotTqg-_I/AAAAAAAAA5c/8lhe3kY4jzc/s80/Dark+Skies+%282013%29+Movie+Review.jpg" height="75" width="47">
    patron ='<td class="contenido"><a href="([^"]+)"><img src="([^"]+)" style="padding: 5px;" alt="[^"]+" title="([^"]+)" height="200" align="left" border="0" width="140"></a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        
        parsed_url = urlparse.urlparse(scrapedurl)
        scrapedtitle = scrapedtitle.replace("Ver Película","")
        scrapedtitle = scrapedtitle.replace("Online Gratis","")

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" , folder=True) )

    return itemlist
       
def peliculas(item):
    logger.info("[cinetux.py] peliculas")
    itemlist = []

    # Descarga la página
    data = anti_cloudflare(item.url)

    '''
    <div style="width: 620px; padding: 0; margin-left: 10px;"><center><div id="post-18159">
    <!--PELICULA--><div class="movielist textcenter">
    <div id="titlecat"><a href="http://www.cinetux.org/2013/03/ver-pelicula-juramento-de-venganza-online-gratis-2009.html" rel="bookmark" title="Ver Película Juramento de Venganza Online Gratis (2009)"><img style="border: 1px solid #FDC101; padding: 1px;" width="130" height="190" src=http://1.bp.blogspot.com/_qNP_wQsK6pg/S4bJOWtjwII/AAAAAAAAALQ/3L0f3yP5c4g/s320/197276.jpg />
    <div style="margin-top:2px;">Ver Película Juramen...</div>
    </a></div>
    <div style="margin-top:5px;margin-bottom:5px;"><span class="rating"><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_off.png" alt="0 votes, average: 0,00 out of 5" title="0 votes, average: 0,00 out of 5" class="post-ratings-image" /><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_off.png" alt="0 votes, average: 0,00 out of 5" title="0 votes, average: 0,00 out of 5" class="post-ratings-image" /><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_off.png" alt="0 votes, average: 0,00 out of 5" title="0 votes, average: 0,00 out of 5" class="post-ratings-image" /><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_off.png" alt="0 votes, average: 0,00 out of 5" title="0 votes, average: 0,00 out of 5" class="post-ratings-image" /><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_off.png" alt="0 votes, average: 0,00 out of 5" title="0 votes, average: 0,00 out of 5" class="post-ratings-image" /></span></div>
    <center><span class="linkcat"><a href="http://www.cinetux.org/genero/thriller" title="Ver todas las entradas en Thriller" rel="category tag">Thriller</a></span></center>
    </div>
    <!--FIN PELICULA-->
    </div><!-- POST META 18159 END -->
    </center></div>
    '''

    # Extrae las entradas (carpetas)
    patron  = '<div class="movielist textcenter[^<]+'
    patron += '<div id="titlecat[^<]+<a href="([^"]+)" rel="bookmark" title="([^"]+)"><img style="[^"]+" width="[^"]+" height="[^"]+" src=(.*?) /[^<]+'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("[cinetux.py] peliculas [patron 1]")
    scrapertools.printMatches(matches)

    for scrapedurl,title,thumbnail in matches:
        scrapedplot = ""
        scrapedthumbnail = thumbnail[:-2]
        scrapedtitle = title[14:]
        scrapedtitle = scrapedtitle.replace("Online Gratis","")
        scrapedtitle = scrapedtitle.replace("Online 2015 Gratis","")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg", folder=True, hasContentDetails="true", contentTitle=scrapedtitle, contentThumbnail=scrapedthumbnail) )


    '''
    <div class="peli_item textcenter">
    <div class="pelicula_img"><a href="http://www.cinetux.org/2013/01/ver-pelicula-la-matanza-de-texas-3d-online-gratis-2013.html"><img alt="" src="http://1.bp.blogspot.com/-Rg9cCqo9Akg/UWub17Y4jVI/AAAAAAAAFo0/jp-8bQVxTB4/s200/La+Masacre+De+Texas+3D.jpg" width="104" height="150" /></a></div>
    <div class="dvdrip"> </div>
    <p><span class="rosa">DVD-RIP</span><br /><span class="icos_lg"><img style="border: 0pt none;" alt="" src="http://4.bp.blogspot.com/-qVqs0f0dsoM/UVJ2-nPN6MI/AAAAAAAAB_8/NkYdkmM-uvY/s320/lat.png" /><img style="border: 0pt none;" alt="" src="http://3.bp.blogspot.com/-t8w6a8_Hk-w/TeA7nd5Ad9I/AAAAAAAADNI/UYV40sR_sfc/s16/online.png" /><img style="border: 0pt none;" alt="" src="https://lh5.googleusercontent.com/-35yef7ubBv8/TeA7nNfUXJI/AAAAAAAADM0/RCQqAiWLX9o/s16/descarga.png" /></span></p>
    <div class="calidad5"> </div>
    <p>&nbsp;</p>
    </div>
    '''

    patron  = '<div class="peli_item textcenter"[^<]+'
    patron += '<div class="pelicula_img"[^<]+'
    patron += '<a href="([^"]+)[^<]+<img alt="" src="([^"]+)".*?'
    patron += '<span class="rosa">(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("[cinetux.py] peliculas [patron 2]")
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,calidad in matches:
        partes = scrapedurl.split("/")
        titulo = partes[len(partes)-1]
        titulo = titulo.replace("ver-pelicula","")
        titulo = titulo.replace("online-gratis","")
        titulo = titulo.replace(".html","")
        titulo = titulo.replace("-"," ")
        titulo = titulo.strip().capitalize()

        scrapedplot = ""
        scrapedtitle = titulo + " ["+calidad+"]"
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg",  folder=True, hasContentDetails="true", contentTitle=scrapedtitle, contentThumbnail=scrapedthumbnail) )

    '''
    <div id="post-57573">
    <div class="itemarchive itemarchive_ie"><a href="http://www.cinetux.org/2014/08/ver-pelicula-tron-legacy-online-gratis-2010.html" rel="bookmark" title="Ver Película TRON: Legacy Online Gratis (2010)"><img style="border: 1px solid #FFFF00; padding: 2px;" width="150" height="205" src=http://4.bp.blogspot.com/_HeR0kdSfWC4/TSPIYcDNW4I/AAAAAAAALDY/WhA3qs_-jvo/s320/tron_legacy9.jpg /></a></div>
    </div><!-- POST META 57573 END -->
    '''
    patron  = '<div id="post-\d+"[^<]+'
    patron += '<div class="i[^<]+'
    patron += '<a href="([^"]+)" rel="[^"]+" title="([^"]+)"[^<]+'
    patron += '<img style="[^"]+" width="\d+" height="\d+" src=([^>]+)>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("[cinetux.py] peliculas [patron 3]")
    scrapertools.printMatches(matches)

    for scrapedurl,title,thumbnail in matches:
        scrapedplot = ""
        scrapedthumbnail = thumbnail[:-2]
        scrapedtitle = title[14:]
        scrapedtitle = scrapedtitle.replace("Online Gratis","")
        scrapedtitle = scrapedtitle.replace("Online 2015 Gratis","")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg", folder=True, hasContentDetails="true", contentTitle=scrapedtitle, contentThumbnail=scrapedthumbnail) )

    '''
    <td class="contenido">
    <a href="http://www.cinetux.org/2015/08/ver-pelicula-upsss-donde-esta-noe-ooops-noah-is-gone-online-gratis-2015.html">
    <img 
        src="http://2.bp.blogspot.com/-Mj60_QHkIcw/VWEhjbHY91I/AAAAAAAAFb8/oMx22CB2ML8/s350/ups-1.jpg" 
        style="border: 1px solid #000;margin: 5px; margin-bottom:10px;" 
        alt="Ver Película ¡Upsss! ¿Dónde está Noé&#8230;? (Ooops! Noah is Gone&#8230;) Online Gratis (2015)" title="Ver Película ¡Upsss! ¿Dónde está Noé&#8230;? (Ooops! Noah is Gone&#8230;) Online Gratis (2015)" height="200" align="left" width="140"></a>
    <div id="puntoscinetux"><div style="margin-top:12px; margin-left:95px;"><span class="rating"><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_on.png" alt="4 votes, average: 5,00 out of 5" title="4 votes, average: 5,00 out of 5" class="post-ratings-image"/><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_on.png" alt="4 votes, average: 5,00 out of 5" title="4 votes, average: 5,00 out of 5" class="post-ratings-image"/><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_on.png" alt="4 votes, average: 5,00 out of 5" title="4 votes, average: 5,00 out of 5" class="post-ratings-image"/><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_on.png" alt="4 votes, average: 5,00 out of 5" title="4 votes, average: 5,00 out of 5" class="post-ratings-image"/><img src="http://www.cinetux.org/wp-content/plugins/wp-postratings/images/stars_crystal/rating_on.png" alt="4 votes, average: 5,00 out of 5" title="4 votes, average: 5,00 out of 5" class="post-ratings-image"/></span></div></div>
    <br></br>
    <b>Año de estreno:</b><font color="#0066FF"> <a href="http://www.cinetux.org/ano/2015" rel="tag">2015</a></font><br>
    <b>Actor (es):</b> <font color="#0066FF"><a href="http://www.cinetux.org/actor/animacion-2" rel="tag">Animación</a></font><br>
    <font color="#000000"><b>Género:</b></font> <font color="#0066FF"><a href="http://www.cinetux.org/genero/animacion" rel="category tag">Animacion</a>, <a href="http://www.cinetux.org/genero/aventura" rel="category tag">Aventura</a>, <a href="http://www.cinetux.org/genero/familiar" rel="category tag">Familiar</a>, <a href="http://www.cinetux.org/genero/infantil" rel="category tag">Infantil</a></font><br>
    Sinopsis: Se acerca el Diluvio Universal y Noé ha construido un gran Arca para salvar a una pareja de cada especie animal pero dos Nestrians, padre e hijo, no son admitidos a entrar. La ayuda involuntaria de dos Grymps, madre e hija, les permite colarse en el Arca. Sin embargo, los niños Finny y Leah [&hellip;]...
    <a href="http://www.cinetux.org/2015/08/ver-pelicula-upsss-donde-esta-noe-ooops-noah-is-gone-online-gratis-2015.html" style="font-weight: bold; font-size: 11pt; float:right;"><img src="http://1.bp.blogspot.com/-KEUuDAGf8ag/Uky6siiAdYI/AAAAAAAAn38/t-J3yxgEwvY/s30/WMP_Play_button-740053.png" border="0"> <font color="#0066FF" size="3">VER PELÍCULA</font></a></td>
    <td></td>
    </tr>
    </tbody></table>
    </div>
    '''
    patron  = '<td class="contenido"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)" style="[^"]+" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("[cinetux.py] peliculas [patron 4]")
    scrapertools.printMatches(matches)

    for scrapedurl,thumbnail,title in matches:
        scrapedplot = ""
        scrapedthumbnail = thumbnail
        scrapedtitle = title[14:]
        scrapedtitle = scrapedtitle.replace("Online Gratis","")
        scrapedtitle = scrapedtitle.replace("Online 2015 Gratis","")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg", folder=True, hasContentDetails="true", contentTitle=scrapedtitle, contentThumbnail=scrapedthumbnail) )

    # Extrae el paginador
    next_page_link = scrapertools.find_single_match(data,'<a href="([^"]+)"[^<]+<strong>Siguiente</strong>')
    if next_page_link!="":
        itemlist.append( Item(channel=__channel__, action="peliculas", title=">> Página siguiente" , extra="next_page", url=next_page_link , fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg", folder=True) )

    return itemlist

def bloque(item):
    logger.info("[cinetux.py] bloque")
    itemlist = []

    # Descarga la página
    data = anti_cloudflare(item.url)
    #data = scrapertools.get_match(data,item.extra+'</h6>(.*?)</div>')
    
    #<a target="_blank" href="http://www.cinetux.org/2013/04/ver-pelicula-dark-skies-online-gratis-2013.html"><img style="border:1px solid #FDC101;" src="http://4.bp.blogspot.com/-UlKHsLS3Tsk/URJotTqg-_I/AAAAAAAAA5c/8lhe3kY4jzc/s80/Dark+Skies+%282013%29+Movie+Review.jpg" height="75" width="47">
    patron = '<a target="_blank" href="([^"]+)"><img style="[^"]+" src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        scrapedplot = ""
        
        parsed_url = urlparse.urlparse(scrapedurl)
        fichero = parsed_url.path
        partes = fichero.split("/")
        scrapedtitle = partes[ len(partes)-1 ]
        scrapedtitle = scrapedtitle.replace("ver-pelicula-","")
        scrapedtitle = scrapedtitle.replace("-online-gratis","")
        scrapedtitle = scrapedtitle.replace(".html","")
        scrapedtitle = scrapedtitle.replace("-"," ")
        scrapedtitle = scrapedtitle.capitalize()

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" , folder=True, hasContentDetails="true", contentTitle=scrapedtitle, contentThumbnail=scrapedthumbnail) )

    return itemlist

def generos(item):
    logger.info("[cinetux.py] generos")
    itemlist = []

    # Descarga la página
    data = anti_cloudflare(item.url)
    data = scrapertools.get_match(data,'neros</h6>(.*?)</div>')
    
    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" , folder=True) )

    return itemlist

def tags(item):
    logger.info("[cinetux.py] tags")
    itemlist = []

    # Descarga la página
    data = anti_cloudflare(item.url)
    data = scrapertools.get_match(data,'Tags</h6>(.*?)</div>')
    patron = "<a href='([^']+)'[^>]+>([^<]+)<"
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" , folder=True) )

    return itemlist

def findvideos(item):
    logger.info("[cinetux.py] findvideos")
    itemlist=[]

    # Busca el argumento
    data = anti_cloudflare(item.url)
    logger.info("data="+data)

    item.plot = scrapertools.find_single_match(data,'<td><span class="info">Sinops[^<]+</span>([^<]+)</td>')
    item.plot = scrapertools.htmlclean(item.plot)
    item.contentPlot = item.plot

    patron  = '<tr class="tabletr">[^<]+'
    patron += '<td class="opcion-td"><img[^>]+>([^>]+)</td>[^<]+'
    patron += '<td class="server-td[^>]+>([^<]+)</td>[^<]+'
    patron += '<td class="idioma-td[^>]+>([^<]+)</td>[^<]+'
    patron += '<td class="fuente-td[^>]+>([^<]+)</td>[^<]+'
    patron += '<td class="link-td">(.*?)</td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedtitle,scrapedserver,scrapedlanguage,scrapedquality,scrapedlink in matches:
        title = "Ver "+scrapedtitle+" en "+scrapedserver+" ("+scrapedlanguage+") ("+scrapedquality+")"
        url = scrapedlink
        thumbnail = servertools.guess_server_thumbnail(scrapedserver)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title , fulltitle=item.fulltitle, url=url , thumbnail=thumbnail , plot=plot , fanart="http://pelisalacarta.mimediacenter.info/fanart/cinetux.jpg" , parentContent=item , folder=False) )

    patron  = '<tr class="tabletr">[^<]+'
    patron += '<td class="episode-server[^>]+><img[^>]+>([^>]+)</td>[^<]+'
    patron += '<td class="episode-server-img[^>]+>([^<]+)</td>[^<]+'
    patron += '<td class="episode-lang[^>]+>([^>]+)</td>[^<]+'
    patron += '<td align="center">([^<]+)</td>[^<]+'
    patron += '<td(.*?)</td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedtitle,scrapedserver,scrapedlanguage,scrapedquality,scrapedlink in matches:
        title = "Ver "+scrapedtitle+" en "+scrapedserver+" ("+scrapedlanguage+") ("+scrapedquality+")"
        url = scrapedlink
        thumbnail = servertools.guess_server_thumbnail(scrapedserver)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title , fulltitle=item.fulltitle+" ["+scrapedlanguage+"]["+scrapedquality+"]", url=url , thumbnail=thumbnail , plot=plot , parentContent=item , folder=False) )

    if len(itemlist)==0:
        itemlist = servertools.find_video_items(item=item,data=data)
        i=1
        for videoitem in itemlist:
            videoitem.title = "Ver Opción %d en %s" % (i,videoitem.server)
            videoitem.fulltitle = item.fulltitle
            videoitem.channel=channel=__channel__

    return itemlist

def play(item):
    logger.info("[cinetux.py] play item.url="+item.url)
    itemlist=[]
    itemlist = servertools.find_video_items(item=item,data=item.url)
    i=1
    for videoitem in itemlist:
        videoitem.title = "Mirror %d%s" % (i,videoitem.title)
        videoitem.fulltitle = item.fulltitle
        videoitem.channel=channel=__channel__
        i=i+1

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