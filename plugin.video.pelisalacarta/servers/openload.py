# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.co
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re
from core import scrapertools
from core import logger
from core import config

           
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0',
       'Accept-Encoding': 'none'}


def test_video_exists(page_url):
    logger.info("pelisalacarta.servers.openload test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We are sorry!' in data:
        return False, "[Openload] El archivo no existe o ha sido borrado" 

    return True, ""

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("pelisalacarta.servers.openload url=" + page_url)
    video_urls = []

    video = True
    data = scrapertools.downloadpageWithoutCookies(page_url)

    if "videocontainer" not in data:
        video = False
        url = page_url.replace("/embed/","/f/")
        data = scrapertools.downloadpageWithoutCookies(url)
        text_encode = scrapertools.get_match(data,"Click to start Download.*?<script[^>]+>(.*?)</script")
        text_decode = decode(data)
    else:
        text_encode = scrapertools.get_match(data,"<video[^<]+<script[^>]+>(.*?)</script>")
        text_decode = decode(data)

    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="es"')
    #Header para la descarga
    header_down = "|User-Agent="+headers['User-Agent']+"|"
    if video == True:
        videourl = scrapertools.get_match(text_decode, "(http.*?true)")
        videourl = scrapertools.get_header_from_response(videourl,header_to_get="location")
        videourl = videourl.replace("https://","http://").replace("?mime=true","")
        extension = videourl[-4:]
        video_urls.append([ extension + " [Openload]", videourl+header_down+extension, 0, subtitle])
    else:
        videourl = scrapertools.find_single_match(text_decode, '"href",(?:\s|)\'([^\']+)\'')
        videourl = videourl.replace("https://","http://")
        extension = videourl[-4:]
        video_urls.append([ extension + " [Openload]", videourl+header_down+extension])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.openload %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '//(?:www.)?openload.../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("pelisalacarta.servers.openload find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[Openload]"
        url = 'https://openload.co/embed/%s/' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'openload'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve

def decode(text):
    text = re.sub(r"\s+", "", text)
    data = text.split("+(ﾟДﾟ)[ﾟoﾟ]")[1]
    chars = data.split("+(ﾟДﾟ)[ﾟεﾟ]+")[1:]

    txt = ""
    for char in chars:
        char = char \
            .replace("(oﾟｰﾟo)","u") \
            .replace("c", "0") \
            .replace("(ﾟДﾟ)['0']", "c") \
            .replace("ﾟΘﾟ", "1") \
            .replace("!+[]", "1") \
            .replace("-~", "1+") \
            .replace("o", "3") \
            .replace("_", "3") \
            .replace("ﾟｰﾟ", "4") \
            .replace("(+", "(")
        char = re.sub(r'\((\d)\)', r'\1', char)
        for x in scrapertools.find_multiple_matches(char,'(\(\d\+\d\))'):
            char = char.replace( x, str(eval(x)) )
        for x in scrapertools.find_multiple_matches(char,'(\(\d\^\d\^\d\))'):
            char = char.replace( x, str(eval(x)) )
        for x in scrapertools.find_multiple_matches(char,'(\(\d\+\d\+\d\))'):
            char = char.replace( x, str(eval(x)) )
        for x in scrapertools.find_multiple_matches(char,'(\(\d\+\d\))'):
            char = char.replace( x, str(eval(x)) )
        for x in scrapertools.find_multiple_matches(char,'(\(\d\-\d\))'):
            char = char.replace( x, str(eval(x)) )
        if 'u' not in char: txt+= char + "|"
    txt = txt[:-1].replace('+','')
    txt_result = "".join([ chr(int(n, 8)) for n in txt.split('|') ])
    sum_base = ""
    m3 = False
    if ".toString(" in txt_result:
        if "+(" in  txt_result:
            m3 = True
            sum_base = "+"+scrapertools.find_single_match(txt_result,".toString...(\d+).")
            txt_pre_temp = scrapertools.find_multiple_matches(txt_result,"..(\d),(\d+).")
            txt_temp = [ (n, b) for b ,n in txt_pre_temp ]
        else:
            txt_temp = scrapertools.find_multiple_matches(txt_result, '(\d+)\.0.\w+.([^\)]+).')
        for numero, base in txt_temp:
            code = toString( int(numero), eval(base+sum_base) )
            if m3:
                txt_result = re.sub( r'"|\+', '', txt_result.replace("("+base+","+numero+")", code) )
            else:
                txt_result = re.sub( r"'|\+", '', txt_result.replace(numero+".0.toString("+base+")", code) )
    return txt_result

def toString(number,base):
   string = "0123456789abcdefghijklmnopqrstuvwxyz"
   if number < base:
      return string[number]
   else:
      return toString(number//base,base) + string[number%base]
