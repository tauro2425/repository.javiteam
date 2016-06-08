import xbmc, xbmcgui, xbmcaddon, xbmcplugin, re
import urllib, urllib2
import re, string
import threading
import os
import base64
#from t0mm0.common.addon import Addon
#from t0mm0.common.net import Net
import urlparse
import xbmcplugin
import cookielib

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__icon__        = __addon__.getAddonInfo('icon')
addon_id = 'plugin.player.javiteam'
selfAddon = xbmcaddon.Addon(id=addon_id)

#addon = Addon('plugin.player.javiteam', sys.argv)
#net = Net()

mode =None
play=False

#play = addon.queries.get('play', None)
paramstring=sys.argv[2]
#url = addon.queries.get('playurl', None)
print paramstring
name='PLAYER.JAVITEAM[COLOR lime]M3U[/COLOR]'
proxy_string=None
proxy_use_chunks=True
auth_string=''
streamtype='HDS'
setResolved=False
if paramstring:
    paramstring="".join(paramstring[1:])
    params=urlparse.parse_qs(paramstring)
    url = params['url'][0]
    try:
        name = params['name'][0]
    except:pass

    try:
        proxy_string = params['proxy'][0]
    except:pass
    try:
        auth_string = params['auth'][0]
    except:pass
    print 'auth_string',auth_string
    try:
        streamtype = params['streamtype'][0]
    except:pass
    print 'streamtype',streamtype

    try:
        proxy_use_chunks_temp = params['proxy_for_chunks'][0]
        import json
        proxy_use_chunks=json.loads(proxy_use_chunks_temp)
    except:pass
    
    simpleDownloader=False
    try:
        simpleDownloader_temp = params['simpledownloader'][0]
        import json
        simpleDownloader=json.loads(simpleDownloader_temp)
    except:pass
	
	
    mode='play'

    try:    
        mode =  params['mode'][0]
    except: pass
    maxbitrate=0
    try:
        maxbitrate =  int(params['maxbitrate'][0])
    except: pass
    play=True

    try:
        setResolved = params['setresolved'][0]
        import json
        setResolved=json.loads(setResolved)
    except:setResolved=False
    
def playF4mLink(url,name,proxy=None,use_proxy_for_chunks=False,auth_string=None,streamtype='HDS',setResolved=False):
    from F4mProxy import f4mProxyHelper
    player=f4mProxyHelper()
    #progress = xbmcgui.DialogProgress()
    #progress.create('Starting local proxy')
    if setResolved:
        urltoplay,item=player.playF4mLink(url, name, proxy, use_proxy_for_chunks,maxbitrate,simpleDownloader,auth_string,streamtype,setResolved)
        item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
        player.playF4mLink(url, name, proxy, use_proxy_for_chunks,maxbitrate,simpleDownloader,auth_string,streamtype,setResolved)
    
    return   
    
def getUrl(url, cookieJar=None,post=None,referer=None,isJsonPost=False, acceptsession=None):

    cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
    opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    #opener = urllib2.install_opener(opener)
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    if isJsonPost:
        req.add_header('Content-Type','application/json')
    if acceptsession:
        req.add_header('Accept-Session',acceptsession)
        
    if referer:
        req.add_header('Referer',referer)
    response = opener.open(req,post,timeout=30)
    link=response.read()
    response.close()
    return link;

def getBBCUrl(urlToFetch):
    text=getUrl(urlToFetch)
    bitRate="1500"
    overrideBitrate=selfAddon.getSetting( "bbcBitRateMax" )
    if overrideBitrate<>"": bitRate=overrideBitrate
    bitRate=int(bitRate)
    regstring='href="(.*?)" bitrate="(.*?)"'
    birates=re.findall(regstring, text)
    birates=[(int(j),f) for f,j in birates]
    birates=sorted(birates, key=lambda f: f[0])
    urlsel=''
    for r, url in birates:
        if r<=bitRate:
            ratesel, urlsel=r, url 
        else:
            break
    if urlsel=='': urlsel=birates[1]
    print 'xxxxxxxxx',ratesel, urlsel
    return urlsel
    
    
def GUIEditExportName(name):

    exit = True 
    while (exit):
          kb = xbmc.Keyboard('default', 'heading', True)
          kb.setDefault(name)
          kb.setHeading('Enter Url')
          kb.setHiddenInput(False)
          kb.doModal()
          if (kb.isConfirmed()):
              name  = kb.getText()
              #name_correct = name_confirmed.count(' ')
              #if (name_correct):
              #   GUIInfo(2,__language__(33224)) 
              #else: 
              #     name = name_confirmed
              #     exit = False
          #else:
          #    GUIInfo(2,__language__(33225)) 
          exit = False
    return(name)
    
if mode ==None:
    videos=[]
   
     

    #['http://dummy','Custom']]
    #print videos

    if 1==2: #disable it as these links are not working, not sure why
        req = urllib2.Request('http://www.gzcbn.tv/app/?app=ios&controller=cmsapi&action=pindao')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        ##	print link

        s='title\":\"(.*?)\",\"stream\":\"(.*?)\"'
        #    
        match=re.compile(s).findall(link)
        i=0
        for i in range(len(match)):
            match[i]= (match[i][1].replace('\\/','/'),match[i][0])


        videos+=match #disabled for time being as these are not working
    #print videos
    for (file_link,name,imgurl,maxbitrate,proxy,usechunks) in videos:
        liz=xbmcgui.ListItem(name,iconImage=imgurl, thumbnailImage=imgurl)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )
        #liz.setProperty("IsPlayable","true")
        u = sys.argv[0] + "?" + urllib.urlencode({'url': file_link,'mode':'play','name':name,'maxbitrate':maxbitrate,'proxy':proxy,'proxy_for_chunks':usechunks}) 
        print u
        
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False, )


   
    
elif mode == "play":
    print 'PLAying ',mode,url,setResolved
    if not name in ['Custom','TESTING not F4M'] :
        playF4mLink(url,name, proxy_string, proxy_use_chunks,auth_string,streamtype,setResolved)
    else:
        listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=url )
        xbmc.Player().play( url,listitem)
    
        #newUrl=GUIEditExportName('')
        #if not newUrl=='':
        #    playF4mLink(newUrl,name)




if not play:
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
    
 