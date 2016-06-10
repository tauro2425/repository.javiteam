# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para VK Server
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("[uploadedto.py] test_video_exists(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    
    if "This video has been removed from public access" in data:
        return False,"El archivo ya no esta disponible<br/>en VK (ha sido borrado)"
    else:
        return True,""

# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[vk.py] get_video_url(page_url='%s')" % page_url)
    
    video_urls = []
    
    # Lee la p‡gina y extrae el ID del v’deo
    data = scrapertools.get_match(
         scrapertools.cache_page( page_url ),
         "<param name=.flashvars. value([^>]+)>")
    patron = ";url([^\=]+)\=([^\&]+)\&"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for calidad, media_url in matches:
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:] + " [vk:" + calidad + "]", media_url ] )
                                  
    for video_url in video_urls:
        logger.info("pelisalacarta.servers.streaminto %s - %s" % (video_url[0],video_url[1]))
    
    return video_urls

def get_mp4_video_link(match0,match1,match2,tipo):
    if match0.endswith("/"):
        videourl = "%su%s/videos/%s.%s" % (match0,match1,match2,tipo)
    else:
        videourl = "%s/u%s/videos/%s.%s" % (match0,match1,match2,tipo)
    return videourl

def find_videos(data):
    encontrados = set()
    devuelve = []

    #http://vkontakte.ru/video_ext.php?oid=95855298&id=162902512&hash=4f0d023887f3648e
    #http://vk.com/video_ext.php?oid=70712020&amp;id=159787030&amp;hash=88899d94685174af&amp;hd=3"
    #http://vk.com/video_ext.php?oid=161288347&#038;id=162474656&#038;hash=3b4e73a2c282f9b4&#038;sd
    #http://vk.com/video_ext.php?oid=146263567&id=163818182&hash=2dafe3b87a4da653&sd
    #http://vk.com/video_ext.php?oid=146263567&id=163818182&hash=2dafe3b87a4da653
    #http://vk.com/video_ext.php?oid=-34450039&id=161977144&hash=0305047ffe3c55a8&hd=3
    data = data.replace("&amp;","&")
    data = data.replace("&#038;","&")
    patronvideos = '(/video_ext.php\?oid=[^&]+&id=[^&]+&hash=[a-z0-9]+)'
    logger.info("[vk.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos).findall(data)

    for match in matches:
        titulo = "[vk]"
        url = "http://vk.com"+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vk' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    # http://vk.com/video97482389_161509127?section=all
    patronvideos  = '(vk\.[a-z]+\/video[0-9]+_[0-9]+)'
    logger.info("[vk.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    
    for match in matches:
        titulo = "[vk]"
        url = "http ://"+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vk' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://vk.com/video_ext.php?oid=190230445&id=164616513&hash=ef16fcd83b58b192&hd=1")

    return len(video_urls)>0