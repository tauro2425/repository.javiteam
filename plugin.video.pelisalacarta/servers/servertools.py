# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Utilidades para detectar vídeos de los diferentes conectores
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re,sys
import urllib2

from core import scrapertools
#from core import jsontools
from core import config
from core import logger

# Listas de servidores empleadas a la hora de reproducir para explicarle al usuario por qué no puede ver un vídeo

# Lista de los servidores que se pueden ver sin cuenta premium de ningún tipo
FREE_SERVERS = []
FREE_SERVERS.extend(['directo','allmyvideos','adnstream','divxstage','facebook','fourshared','twitvid'])
FREE_SERVERS.extend(['googlevideo','mediafire','moevideos','movshare','auroravid'])
FREE_SERVERS.extend(['royalvids','sockshare','stagevu','tutv','userporn','veoh','videobam'])
FREE_SERVERS.extend(['vidbux','bitvidsx','vimeo','vk','watchfreeinhd','youtube'])
FREE_SERVERS.extend(['jumbofiles','nowvideo','streamcloud', 'dailymotion', 'vidbull'])
FREE_SERVERS.extend(['nosvideo','videopremium','flashx','upafile', 'zippyshare'])
FREE_SERVERS.extend(['fileflyer','tunepk','powvideo','mega','videomega','vidspot','netutv','rutube'])
FREE_SERVERS.extend(['videozed','documentary', 'firedrive','videott','gamovideo'])
FREE_SERVERS.extend(['torrent','video4you','mailru','streaminto','backin','akstream', 'speedvideo', 'junkyvideo', 'rapidvideo', 'realvid', 'cloudzilla', 'fakingstv'])
FREE_SERVERS.extend(['cumlouder','v4y','streamable','videostoring','youwatch'])
FREE_SERVERS.extend(['vodlocker','thevideome','rocvideo','vidxtreme','vidtome','vidzi','letwatch','sendvid','vkpass','okru','cnubis','yourupload','mp4upload','turbovideos','vimpleru','spruto','openload','idowatch','xvideos'])
FREE_SERVERS.extend(['videowood','thevideos','uptobox','streame','vidgg','allvid','vodbeast','clicknupload','streamplay'])

# Servidores no soportados, pero se ponen como free porque necesitas tener el patrón para poder informar
FREE_SERVERS.extend(['cloudsix'])

# Lista de TODOS los servidores que funcionan con cuenta premium individual
PREMIUM_SERVERS = ['uploadedto','nowvideo','onefichier','filesmonster']

# Lista de TODOS los servidores soportados por Filenium
#FILENIUM_SERVERS = jsontools.load_json(urllib2.urlopen('http://filenium.com/domainsxbmc'))
FILENIUM_SERVERS = []
FILENIUM_SERVERS.extend(["nitroflare","1fichier","mega","allmyvideos","cliphunter","dailymotion","divxstage","facebook","filefactory","filepost","filesmonster","firedrive","gigasize","keep2share","keep2share","letitbit","mediafire","metacafe","mitele","moevideos","netload","nowvideo","oboom","played","pornhub","rapidgator","shareflare","streamcloud","turbobit","uploadable","uploaded","uploaded","userporn","videoweed","vidspot","vimeo","vk","xenubox","youngpornvideos","youtube","zippyshare","lix","safelinking","linkto","2shared","4shared","hugefiles","nowdownload","tusfiles","uploading","uptobox"]);

# Lista de TODOS los servidores soportados por Real-Debrid
REALDEBRID_SERVERS = ['one80upload','tenupload','onefichier','onehostclick','twoshared','fourfastfile','fourshared','abc','asfile','badongo','bitshare','cbscom','crocko','cwtv','dailymotion','dateito',
                    'dengee','diglo','extabit','filedino','filefactory','fileflyer','filekeen','filemade','filemates','fileover','filepost',
                   'filesend','filesmonster','filevelocity','freakshare','free','furk','fyels','gigasize','gigaup','glumbouploads','goldfile','hitfile','hipfile','hostingbulk',
                   'hulu','ifile','jakfile','jumbofiles','letitbit','loadto','mediafire','mega','megashare','megashares','mixturevideo','muchshare','netload',
                   'novafile','nowdownload','purevid','putbit','putlocker','redtube','rapidgator','rapidshare','rutube','ryushare','scribd','sendspace','sharebees','shareflare','shragle','slingfile','sockshare',
                   'soundcloud','speedyshare','turbobit','unibytes','uploadc','uploadedto','uploading','uploadspace','uptobox','openload','clicknupload','youwatch',
                   'userporn','veevr','vidbux','vidxden','vimeo','vipfile','wattv','xfileshare','youporn','youtube','yunfile','zippyshare','nowvideo','filesmonster','oboom','hugefiles','uploadable','bigfile']
#wupload,fileserve

ALLDEBRID_SERVERS = ['one80upload','onefichier','twoshared','fourfastfile','fourshared','albafile','bitshare','crocko','cyberlocker','dailymotion','dengee',
                   'depfile','dlfree','extabit','extmatrix','filefactory','fileflyer','filegag','filehost','fileover','filepost','filerio','filesabc',
                   'filesend','filesmonster','filestay','freakshare','gigasize','jumbofiles','letitbit','loadto','mediafire','megashares','mixturevideo','netload',
                   'nitrobits','oteupload','purevid','putlocker','rapidgator','rapidshare','redtube','scribd','secureupload','sharebees','shareflare','slingfile','sockshare',
                   'soundcloud','speedload','speedyshare','turbobit', 'uloadto', 'uploadc','uploadedto','uploading','uptobox',
                   'userporn','vimeo','vipfile','youporn','youtube','yunfile','zippyshare','filesmonster']
    
# Lista completa de todos los servidores soportados por pelisalacarta, usada para buscar patrones
#ALL_SERVERS = list( set(FREE_SERVERS) | set(FILENIUM_SERVERS) | set(REALDEBRID_SERVERS) | set(ALLDEBRID_SERVERS) )
#ALL_SERVERS.sort()

# Lista de servidores activos en funcion de: Configuracion/Cuentas
if config.get_setting("hidepremium")=="false":
    ENABLED_SERVERS= list( set(FREE_SERVERS) | set(FILENIUM_SERVERS) | set(REALDEBRID_SERVERS) | set(ALLDEBRID_SERVERS) | set(PREMIUM_SERVERS) )
else:
    ENABLED_SERVERS= set(FREE_SERVERS)
    if config.get_setting("uploadedtopremium")=="true":
        ENABLED_SERVERS.add('uploadedto')
    if config.get_setting("nowvideopremium")=="true":
        ENABLED_SERVERS.add('nowvideo')
    if config.get_setting("onefichierpremium")=="true":
        ENABLED_SERVERS.add('onefichier')
    if config.get_setting("fileniumpremium")=="true":
        ENABLED_SERVERS= ENABLED_SERVERS | set(FILENIUM_SERVERS)
    if config.get_setting("realdebridpremium")=="true":
        ENABLED_SERVERS= ENABLED_SERVERS | set(REALDEBRID_SERVERS)
    if config.get_setting("alldebridpremium")=="true":
        ENABLED_SERVERS= ENABLED_SERVERS | set(ALLDEBRID_SERVERS)
    ENABLED_SERVERS= list (ENABLED_SERVERS)
ENABLED_SERVERS.sort()


# Función genérica para encontrar vídeos en una página
def find_video_items(item=None, data=None, channel=""):
    logger.info("[servertools.py] find_video_items")

    # Descarga la página
    if data is None:
        from core import scrapertools
        data = scrapertools.cache_page(item.url)
        #logger.info(data)

    # Busca los enlaces a los videos
    from core.item import Item
    from servers import servertools
    listavideos = servertools.findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        scrapedtitle = "Enlace encontrado en "+video[2]
        scrapedurl = video[1]
        server = video[2]
        thumbnail = "http://media.tvalacarta.info/servers/server_"+server+".png"
        
        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="play" , server=server, url=scrapedurl, thumbnail=thumbnail, show=item.show , plot=item.plot , parentContent=item, folder=False) )

    return itemlist

def guess_server_thumbnail(title):
    logger.info("[servertools.py] guess_server_thumbnail title="+title)

    lowcase_title = title.lower()

    if "netu" in lowcase_title:
        logger.info("[servertools.py] guess_server_thumbnail caso especial netutv")
        return "http://media.tvalacarta.info/servers/server_netutv.png"

    if "ul.to" in lowcase_title:
        logger.info("[servertools.py] guess_server_thumbnail caso especial ul.to")
        return "http://media.tvalacarta.info/servers/server_uploadedto.png"

    if "waaw" in lowcase_title:
        logger.info("[servertools.py] guess_server_thumbnail caso especial waaw")
        return "http://media.tvalacarta.info/servers/server_waaw.png"

    if "streamin" in lowcase_title:
        logger.info("[servertools.py] guess_server_thumbnail caso especial streamin")
        return "http://media.tvalacarta.info/servers/server_streaminto.png"

    for serverid in ENABLED_SERVERS:
        if serverid in lowcase_title:
            logger.info("[servertools.py] guess_server_thumbnail encontrado "+serverid)
            return "http://media.tvalacarta.info/servers/server_"+serverid+".png"

    return ""

def findvideosbyserver(data, serverid):
    logger.info("[servertools.py] findvideos")
    encontrados = set()
    devuelve = []
    try:
        exec "from servers import "+serverid
        exec "devuelve.extend("+serverid+".find_videos(data))"
    except ImportError:
        logger.info("No existe conector para #"+serverid+"#")
        #import traceback
        #logger.info(traceback.format_exc())
    except:
        logger.info("Error en el conector #"+serverid+"#")
        import traceback
        logger.info(traceback.format_exc())

    return devuelve

def findvideos(data):
    logger.info("[servertools.py] findvideos") # en #"+data+"#")
    encontrados = set()
    devuelve = []

    # Ejecuta el findvideos en cada servidor
    #for serverid in ALL_SERVERS:
    for serverid in ENABLED_SERVERS:
        try:
            # Sustituye el código por otro "Plex compatible"
            #exec "from servers import "+serverid
            #exec "devuelve.extend("+serverid+".find_videos(data))"
            servers_module = __import__("servers."+serverid)
            server_module = getattr(servers_module,serverid)
            devuelve.extend( server_module.find_videos(data) )
        except ImportError:
            logger.info("No existe conector para #"+serverid+"#")
            #import traceback
            #logger.info(traceback.format_exc())
        except:
            logger.info("Error en el conector #"+serverid+"#")
            import traceback
            logger.info(traceback.format_exc())

    return devuelve

def get_video_urls(server,url):
    '''
    servers_module = __import__("servers."+server)
    server_module = getattr(servers_module,server)
    return server_module.get_video_url( page_url=url)
    '''

    video_urls,puede,motivo = resolve_video_urls_for_playing(server,url)
    return video_urls

def get_channel_module(channel_name):
    channels_module = __import__("channels."+channel_name)
    channel_module = getattr(channels_module,channel_name)
    return channel_module

def get_server_from_url(url):
    encontrado = findvideos(url)
    if len(encontrado)>0:
        devuelve = encontrado[0][2]
    else:
        devuelve = "directo"

    return devuelve

def resolve_video_urls_for_playing(server,url,video_password="",muestra_dialogo=False):
    logger.info("[servertools.py] resolve_video_urls_for_playing, server="+server+", url="+url)
    video_urls = []
    torrent = False
    
    server = server.lower()

    # Si el vídeo es "directo", no hay que buscar más
    if server=="directo" or server=="local":
        logger.info("[servertools.py] server=directo, la url es la buena")
        
        try:
            import urlparse
            parsed_url = urlparse.urlparse(url)
            logger.info("parsed_url="+str(parsed_url))
            extension = parsed_url.path[-4:]
        except:
            extension = url[-4:]

        video_urls = [[ "%s [%s]" % (extension,server) , url ]]
        return video_urls,True,""

    # Averigua las URL de los vídeos
    else:
        
        #if server=="torrent":
        #    server="filenium"
        #    torrent = True

        # Carga el conector
        try:
            # Muestra un diálogo de progreso
            if muestra_dialogo:
                import xbmcgui
                progreso = xbmcgui.DialogProgress()
                progreso.create( "pelisalacarta" , "Conectando con "+server)

            # Sustituye el código por otro "Plex compatible"
            #exec "from servers import "+server+" as server_connector"
            servers_module = __import__("servers."+server)
            server_connector = getattr(servers_module,server)

            logger.info("[servertools.py] servidor de "+server+" importado")
            if muestra_dialogo:
                progreso.update( 20 , "Conectando con "+server)

            # Si tiene una función para ver si el vídeo existe, lo comprueba ahora
            if hasattr(server_connector, 'test_video_exists'):
                logger.info("[servertools.py] invocando a "+server+".test_video_exists")
                puedes,motivo = server_connector.test_video_exists( page_url=url )

                # Si la funcion dice que no existe, fin
                if not puedes:
                    logger.info("[servertools.py] test_video_exists dice que el video no existe")
                    if muestra_dialogo: progreso.close()
                    return video_urls,puedes,motivo
                else:
                    logger.info("[servertools.py] test_video_exists dice que el video SI existe")

            # Obtiene enlaces free
            if server in FREE_SERVERS:
                logger.info("[servertools.py] invocando a "+server+".get_video_url")
                video_urls = server_connector.get_video_url( page_url=url , video_password=video_password )
                
                # Si no se encuentran vídeos en modo free, es porque el vídeo no existe
                if len(video_urls)==0:
                    if muestra_dialogo: progreso.close()
                    return video_urls,False,"No se puede encontrar el vídeo en "+server

            # Obtiene enlaces premium si tienes cuenta en el server
            if server in PREMIUM_SERVERS and config.get_setting(server+"premium")=="true":
                video_urls = server_connector.get_video_url( page_url=url , premium=(config.get_setting(server+"premium")=="true") , user=config.get_setting(server+"user") , password=config.get_setting(server+"password"), video_password=video_password )
                
                # Si no se encuentran vídeos en modo premium directo, es porque el vídeo no existe
                if len(video_urls)==0:
                    if muestra_dialogo: progreso.close()
                    return video_urls,False,"No se puede encontrar el vídeo en "+server
    
            # Obtiene enlaces filenium si tienes cuenta
            if server in FILENIUM_SERVERS and config.get_setting("fileniumpremium")=="true":
    
                # Muestra un diálogo de progreso
                if muestra_dialogo:
                    progreso.update( 40 , "Conectando con Filenium")
    
                from servers import filenium as gen_conector
                
                video_gen = gen_conector.get_video_url( page_url=url , premium=(config.get_setting("fileniumpremium")=="true") , user=config.get_setting("fileniumuser") , password=config.get_setting("fileniumpassword"), video_password=video_password )
                extension = gen_conector.get_file_extension(video_gen)
                logger.info("[xbmctools.py] filenium url="+video_gen)
                video_urls.append( [ extension+" ["+server+"][filenium]", video_gen ] )

            # Obtiene enlaces realdebrid si tienes cuenta
            if server in REALDEBRID_SERVERS and config.get_setting("realdebridpremium")=="true":
    
                # Muestra un diálogo de progreso
                if muestra_dialogo:
                    progreso.update( 60 , "Conectando con Real-Debrid")

                from servers import realdebrid as gen_conector
                video_gen = gen_conector.get_video_url( page_url=url , premium=(config.get_setting("realdebridpremium")=="true") , user=config.get_setting("realdebriduser") , password=config.get_setting("realdebridpassword"), video_password=video_password )
                logger.info("[xbmctools.py] realdebrid url="+video_gen)
                if not "REAL-DEBRID" in video_gen:
                    video_urls.append( [ "."+video_gen.rsplit('.',1)[1]+" [realdebrid]", video_gen ] )
                else:
                    if muestra_dialogo: progreso.close()
                    # Si RealDebrid da error pero tienes un enlace válido, no te dice nada
                    if len(video_urls)==0:
                        return video_urls,False,video_gen
                  
            # Obtiene enlaces alldebrid si tienes cuenta
            if server in ALLDEBRID_SERVERS and config.get_setting("alldebridpremium")=="true":
    
                # Muestra un diálogo de progreso
                if muestra_dialogo:
                    progreso.update( 80 , "Conectando con All-Debrid")

                from servers import alldebrid as gen_conector
                video_gen = gen_conector.get_video_url( page_url=url , premium=(config.get_setting("alldebridpremium")=="true") , user=config.get_setting("alldebriduser") , password=config.get_setting("alldebridpassword"), video_password=video_password )
                logger.info("[xbmctools.py] alldebrid url="+video_gen)
                if video_gen.startswith("http"):
                    video_urls.append( [ "."+video_gen.rsplit('.',1)[1]+" [alldebrid]", video_gen ] )
                else:
                    # Si Alldebrid da error pero tienes un enlace válido, no te dice nada
                    if len(video_urls)==0:
                        return [],False,video_gen.strip()

            
            if muestra_dialogo:
                progreso.update( 100 , "Proceso finalizado")

            # Cierra el diálogo de progreso
            if muestra_dialogo: progreso.close()

            # Llegas hasta aquí y no tienes ningún enlace para ver, así que no vas a poder ver el vídeo
            if len(video_urls)==0:
                # ¿Cual es el motivo?
                
                # 1) No existe -> Ya está controlado
                # 2) No tienes alguna de las cuentas premium compatibles

                # Lista de las cuentas que soportan este servidor
                listapremium = ""
                if server in ALLDEBRID_SERVERS: listapremium+="All-Debrid o "            
                if server in FILENIUM_SERVERS: listapremium+="Filenium o "
                if server in REALDEBRID_SERVERS: listapremium+="Real-Debrid o "
                if server in PREMIUM_SERVERS: listapremium+=server+" o "
                listapremium = listapremium[:-3]
    
                return video_urls,False,"Para ver un vídeo en "+server+" necesitas<br/>una cuenta en "+listapremium

        except:
            if muestra_dialogo: progreso.close()
            import traceback
            from pprint import pprint
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            for line in lines:
                line_splits = line.split("\n")
                for line_split in line_splits:
                    logger.error(line_split)

            return video_urls,False,"Se ha producido un error en<br/>el conector con "+server

    return video_urls,True,""
    
def is_server_enabled (server):
    server=scrapertools.find_single_match(server,'([^\.]+)')
    return server in ENABLED_SERVERS
  
