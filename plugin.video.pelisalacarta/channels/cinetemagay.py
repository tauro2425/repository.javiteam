# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cinetemagay.com por sdfasd
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

#from pelisalacarta import buscador

__channel__ = "cinetemagay"
__category__ = "D"
__type__ = "generic"
__title__ = "cinetemagay"
__language__ = "ES"

DEBUG = config.get_setting("debug")

IMAGES_PATH = os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'cinetemagay' )

def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)
    
def isGeneric():
    return True

def mainlist(item):
    logger.info("[cinetemagay.py] mainlist")

    itemlist = []     
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Cine gay latinoamericano" , url="http://cinegaylatinoamericano.blogspot.com.es/feeds/posts/default/?max-results=100&start-index=1",thumbnail="http://www.americaeconomia.com/sites/default/files/imagecache/foto_nota/homosexual1.jpg"))       
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Cine y cortos gay" , url="http://cineycortosgay.blogspot.com.es/feeds/posts/default/?max-results=100&start-index=1",thumbnail="http://www.elmolar.org/wp-content/uploads/2015/05/cortometraje.jpg"))    
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Cine gay online (México)" , url="http://cinegayonlinemexico.blogspot.com.es/feeds/posts/default/?max-results=100&start-index=1",thumbnail="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmmqL6tS2Ced1VoxlGQT0q-ibPEz1DCV3E1waHFDI5KT0pg1lJ"))                           
    itemlist.append( Item(channel=__channel__, action="lista"  , title="Sentido gay" , url="http://www.sentidogay.blogspot.com.es//feeds/posts/default/?max-results=100&start-index=1",thumbnail="http://1.bp.blogspot.com/-epOPgDD_MQw/VPGZGQOou1I/AAAAAAAAAkI/lC25GrukDuo/s1048/SentidoGay.jpg"))               
    itemlist.append( Item(channel=__channel__, action="lista"  , title="PGPA" , url="http://pgpa.blogspot.com.es/feeds/posts/default/?max-results=100&start-index=1",thumbnail="http://themes.googleusercontent.com/image?id=0BwVBOzw_-hbMNTRlZjk2YWMtYTVlMC00ZjZjLWI3OWEtMWEzZDEzYWVjZmQ4"))               
         
    return itemlist









def lista(item):
    logger.info("[cinetemagay.py] lista")
    itemlist = []

   
  
         
    # Descarga la pagina
    
    data = scrapertools.cache_page(item.url)
    
    #logger.info(data)



    # Extrae las entradas (carpetas)
  
 
    patronvideos  ='&lt;img .*?src=&quot;(.*?)&quot;'
    patronvideos += "(.*?)<link rel='alternate' type='text/html' href='([^']+)' title='([^']+)'.*?>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)


    for match in matches:
        scrapedtitle = match[3]
        scrapedtitle = scrapedtitle.replace("&apos;","'")
        scrapedtitle = scrapedtitle.replace("&quot;","'")
        scrapedtitle = scrapedtitle.replace("&amp;amp;","'")
        scrapedtitle = scrapedtitle.replace("&amp;#39;","'")
        scrapedurl = match[2]
        scrapedthumbnail = match[0]
        imagen = ""
        scrapedplot = match[1]  
        tipo = match[1]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        scrapedplot = "<"+scrapedplot    
        scrapedplot = scrapedplot.replace("&gt;",">")
        scrapedplot = scrapedplot.replace("&lt;","<")
        scrapedplot = scrapedplot.replace("</div>","\n")
        scrapedplot = scrapedplot.replace("<br />","\n")
        scrapedplot = scrapedplot.replace("&amp;","")
        scrapedplot = scrapedplot.replace("nbsp;","")
        scrapedplot=strip_tags(scrapedplot)
        itemlist.append( Item(channel=__channel__, action="detail", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedurl+scrapedplot , folder=True) )
   

    variable = item.url.split("index=")[1]
    variable=int(variable)
    variable+=100
    variable=str(variable)
    variable_url = item.url.split("index=")[0]
    url_nueva=variable_url+"index="+variable
    itemlist.append( Item(channel=__channel__, action="lista", title="Ir a la página siguiente (desde "+variable+")" , url=url_nueva , thumbnail="" , plot="Pasar a la pÃ¡gina siguiente (en grupos de 100)\n\n"+url_nueva) )
   
    return itemlist









def detail(item):
    logger.info("[cinetemagay.py] detail")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cachePage(item.url)


    data =data.replace("%3A", ":")
    data =data.replace("%2F", "/")
    data =data.replace("%3D", "=")   
    data =data.replace("%3", "?")   
    data =data.replace("%26", "&")
    descripcion = ""
    plot = ""
    patrondescrip = 'SINOPSIS:(.*?)'
    matches = re.compile(patrondescrip,re.DOTALL).findall(data)
    if len(matches)>0:
        descripcion = matches[0]
        descripcion = descripcion.replace("&nbsp;","")
        descripcion = descripcion.replace("<br/>","")
        descripcion = descripcion.replace("\r","")
        descripcion = descripcion.replace("\n"," ")
        descripcion = descripcion.replace("\t"," ")
        descripcion = re.sub("<[^>]+>"," ",descripcion)
        descripcion = descripcion
        try :
            plot = unicode( descripcion, "utf-8" ).encode("iso-8859-1")
        except:
            plot = descripcion


   
        
    # Busca los enlaces a los videos de  servidores
    video_itemlist = servertools.find_video_items(data=data)
    for video_item in video_itemlist:

        itemlist.append( Item(channel=__channel__ , action="play" , server=video_item.server, title=item.title+"  "+video_item.title,url=video_item.url, thumbnail=item.thumbnail, plot=video_item.url, folder=False))



    return itemlist




# VerificaciÃ³n automÃ¡tica de canales: Esta funciÃ³n debe devolver "True" si estÃ¡ ok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vÃ­deos de "Novedades" devuelve mirrors
    onesite_items = lista(mainlist_items[0])
    bien = False
    for onesite_item in onesite_items:
        mirrors = servertools.find_video_items( item=onesite_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
