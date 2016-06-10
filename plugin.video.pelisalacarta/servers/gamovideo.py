# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para gamovideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

headers = [["User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"]]

def test_video_exists( page_url ):
    logger.info("pelisalacarta.servers.gamovideo test_video_exists(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url, headers=headers)

    if ("File was deleted" or "Not Found") in data:
        return False, "[Gamovideo] El archivo no existe o ha sido borrado" 

    return True, ""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.gamovideo get_video_url(page_url='%s')" % page_url)
    if not "embed" in page_url:
        page_url = page_url.replace("http://gamovideo.com/","http://gamovideo.com/embed-") + ".html"

    data = scrapertools.cache_page(page_url,headers=headers)
    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    data = jsunpack.unpack(data)

    host = scrapertools.get_match(data, 'image:"(http://[^/]+/)')
    flv_url = scrapertools.get_match(data, ',\{file:"([^"]+)"')
    rtmp_url = scrapertools.get_match(data, '\[\{file:"([^"]+)"')
    flv = host+flv_url.split("=")[1]+"/v.flv"

    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(flv)[-4:]+" [gamovideo]",flv])
    #video_urls.append(["RTMP [gamovideo]",rtmp_url])      

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.gamovideo %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://gamovideo.com/auoxxtvyoy
    # http://gamovideo.com/h1gvpjarjv88
    # http://gamovideo.com/embed-sbb9ptsfqca2-588x360.html
    patronvideos  = 'gamovideo.com/(?:embed-|)([a-z0-9]+)'
    logger.info("pelisalacarta.servers.gamovideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[gamovideo]"
        url = "http://gamovideo.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'gamovideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://gamovideo.com/91zidptmfqnr")

    return len(video_urls)>0
