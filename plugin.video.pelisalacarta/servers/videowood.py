# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for videowood.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re

from core import scrapertools
from core import logger
from core import jsunpack


def test_video_exists(page_url):
    logger.info("pelisalacarta.servers.videowood test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video doesn't exist." in data:
        return False, 'The requested video was not found.'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("pelisalacarta.servers.videowood url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    data = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    data = jsunpack.unpack(data).replace("\\","")


    # URL del vídeo
    pattern = r'"file"\s*:\s*"([^"]+/video/[^"]+)'
    match = re.search(pattern, data, re.DOTALL)

    url = match.group(1)
    video_urls.append([url[-4:] + " [Videowood]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"https?://(?:www.)?videowood.tv/(?:embed/|video/)[0-9a-z]+"
    logger.info("pelisalacarta.servers.videowood find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for url in matches:
        titulo = "[Videowood]"
        url = url.replace('/video/', '/embed/')
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'videowood'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve