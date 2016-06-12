#
#      Copyright (C) 2014 Richard Dean
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc
import xbmcaddon
import xbmcgui
import os
import re
import dixie
import requests
import cookielib
import pickle
import time
import datetime


ADDONID     = 'script.tvguidedixie'
ADDON       =  xbmcaddon.Addon(ADDONID)
HOME        =  ADDON.getAddonInfo('path')
ICON        =  os.path.join(HOME, 'icon.png')
ICON        =  xbmc.translatePath(ICON)
PROFILE     =  xbmc.translatePath(ADDON.getAddonInfo('profile'))
RESOURCES   =  os.path.join(HOME, 'resources')

def SetSetting(param, value):
    xbmcaddon.Addon(ADDONID).setSetting(param, str(value))


def GetSetting(param):
    return xbmcaddon.Addon(ADDONID).getSetting(param)

DIXIEURL    =  GetSetting('dixie.url').upper()
DIXIELOGOS  =  GetSetting('dixie.logo.folder')
SKIN        =  GetSetting('dixie.skin')
FILMON      =  GetSetting('FILMON')
VERSION     =  ADDON.getAddonInfo('version')
TITLE       = 'OnTapp.TV'
SKINVERSION = '15'
INIVERSION  = '1'
DEBUG       = GetSetting('DEBUG') == 'true'

datapath   = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookiepath = os.path.join(datapath, 'cookies')
cookiefile = os.path.join(cookiepath, 'cookie')

if not os.path.exists(cookiepath):
    os.makedirs(cookiepath)


def log(text):
    try:
        output = '%s V%s : %s' % (TITLE, VERSION, str(text))
        if DEBUG:
            xbmc.log(output)
        else:
            xbmc.log(output, xbmc.LOGDEBUG)
    except:
        pass


def notify(message, length=5000):
    cmd = 'XBMC.notification(%s,%s,%d,%s)' % (TITLE, message, length, ICON)
    xbmc.executebuiltin(cmd)


ooOOOoo = ''
def ttTTtt(i, t1, t2=[]):
 t = ooOOOoo
 for c in t1:
  t += chr(c)
  i += 1
  if i > 1:
   t = t[:-1]
   i = 0  
 for c in t2:
  t += chr(c)
  i += 1
  if i > 1:
   t = t[:-1]
   i = 0
 return t


baseurl  = ttTTtt(0,[104,244,116,66,116,68,112,168,115,206,58,5,47,99,47,49,119,205,119,250,119,63,46,15,111,225,110,222,45],[146,116,128,97,158,112,30,112,118,46,72,116,230,118,137,47,191,63,67,115,190,50,69,109,50,101,166,109,23,98,77,101,104,114,82,95,190,102,59,105,74,108,247,101,196,95,213,114,210,101,191,109,217,111,155,116,243,101,87,61,243,121,83,101,149,115,40,38,96,115,62,50,39,109,151,101,197,109,163,98,217,101,220,114,80,95,16,102,156,105,72,108,151,101,52,95,170,100,111,111,99,119,206,110,216,108,201,111,111,97,183,100,227,61,89,47,77,97,165,99,233,99,245,101,255,115,69,115,150,45,217,115,81,50,118,109,152,101,39,109,102,98,114,101,125,114,14,45,8,108,85,101,80,118,252,101,79,108,63,49,129,47])
resource = ttTTtt(0,[104,229,116,71,116,131,112,130,115],[164,58,247,47,243,47,178,119,209,119,132,119,192,46,155,111,36,110,223,45,89,116,143,97,161,112,156,112,39,46,173,116,225,118,126,47,102,119,13,112,241,45,163,99,12,111,122,110,91,116,140,101,66,110,153,116,80,47,134,117,66,112,86,108,157,111,41,97,89,100,189,115,87,47])
loginurl = ttTTtt(393,[72,104,176,116],[194,116,1,112,40,115,24,58,196,47,96,47,160,119,10,119,73,119,153,46,156,111,245,110,246,45,163,116,51,97,57,112,60,112,217,46,1,116,38,118,110,47,202,119,147,112,232,45,135,108,73,111,70,103,215,105,209,110,244,46,121,112,128,104,196,112])


def GetDixieUrl(DIXIEURL):
    if DIXIEURL == 'ALL CHANNELS':
        return baseurl + 'all/'


def GetExtraUrl():
    return resource


def GetLoginUrl():
    return loginurl


def GetGMTOffset():
    gmt = GetSetting('gmtfrom').replace('GMT', '')

    if gmt == '':
        offset = 0
    else:
        offset = int(gmt)

    return datetime.timedelta(hours = offset)


def saveCookies(requests_cookiejar, filename):
    with open(cookiefile, 'wb') as f:
        pickle.dump(requests_cookiejar, f)


def loadCookies(filename):
    if not os.path.isfile(cookiefile):
        os.makedirs(cookiepath)
        open(cookiefile, 'a').close
        
    with open(cookiefile, 'rb') as f:
        return pickle.load(f)


def resetCookies():
    try:
        if os.path.isfile(cookiefile):
            os.remove(cookiefile)
    except: pass



def getPreviousTime():
    time_object = xbmcgui.Window(10000).getProperty('OTT_LOGIN_TIME')
    
    if time_object == '':
        time_object = '2001-01-01 00:00:00'
        
    previousTime = parseTime(time_object)
    
    return previousTime


def parseTime(when):
    if type(when) in [str, unicode]:
        dt = when.split(' ')
        d  = dt[0]
        t  = dt[1]
        ds = d.split('-')
        ts = t.split(':')
        when = datetime.datetime(int(ds[0]), int(ds[1]) ,int(ds[2]), int(ts[0]), int(ts[1]), int(ts[2].split('.')[0]))
        
    return when


def validToRun(silent=False):
    previousTime = getPreviousTime()
    now          = datetime.datetime.today()
    delta        = now - previousTime
    nSeconds     = (delta.days * 86400) + delta.seconds
    
    if nSeconds > 35 * 60:        
        if not doLogin(silent):
            return False

        xbmcgui.Window(10000).setProperty('OTT_LOGIN_TIME', str(now))
        
    return True


def doLogin(silent=False):
    log ('************ On-Tapp.TV Login ************')
    with requests.Session() as s:
        try:    s.get(GetLoginUrl())
        except: return False

        USERNAME    =  GetSetting('username')
        PASSWORD    =  GetSetting('password')
        PAYLOAD     =  { 'log' : USERNAME, 'pwd' : PASSWORD, 'wp-submit' : 'Log In' }

        code = 'login_error'

        if USERNAME and PASSWORD:        
            login = s.post(GetLoginUrl(), data=PAYLOAD)
            code  = login.content
            saveCookies(s.cookies, cookiefile)
        
        if ('Are you lost' not in code) and ('login_error' not in code):
            message = 'Logged into On-Tapp.TV'
            log(message)
            if not silent:
                notify(message)
            
            return True
            
        try:
            error = re.compile('<div id="login_error">(.+?)<br />').search(code).groups(1)[0]
            error = error.replace('<strong>',  '')
            error = error.replace('</strong>', '')
            error = error.replace('<a href="http://www.on-tapp.tv/wp-login.php?action=lostpassword">Lost your password</a>?', '')
            error = error.strip()
        except:
            error = ''

        message = 'There was a problem logging into On-Tapp.TV.'
        #notify(message)
        log(message + ' : ' + error)
        if not silent:
            DialogOK(message, '', error)
        
        return False


def GetCats():
    import urllib

    path = os.path.join(PROFILE, 'cats.xml')
    url  = GetExtraUrl() + 'resources/cats.xml'

    try:
        urllib.urlretrieve(url, path)
    except:
        pass


def GetChannels():
    path = os.path.join(PROFILE , 'chan.xml')
    url  = GetDixieUrl(DIXIEURL) + 'chan.xml'

    r = requests.get(url, cookies=loadCookies(cookiefile))
    
    with open(path, 'wb') as f:
        for chunk in r.iter_content(512):
            f.write(chunk)

    return path


def ShowBusy(hideProgress=True):
    try:
        busy = xbmcgui.WindowXMLDialog('DialogBusy.xml', '')
        busy.show()

        if hideProgress:
            try:    busy.getControl(10).setVisible(False)
            except: pass

        return busy
    except:
        pass

    return None



def DialogOK(line1, line2='', line3=''):
    d = xbmcgui.Dialog()
    d.ok(TITLE + ' - ' + VERSION, line1, line2 , line3)


def DialogYesNo(line1, line2='', line3='', noLabel=None, yesLabel=None):
    d = xbmcgui.Dialog()
    if noLabel == None or yesLabel == None:
        return d.yesno(TITLE + ' - ' + VERSION, line1, line2 , line3) == True
    else:
        return d.yesno(TITLE + ' - ' + VERSION, line1, line2 , line3, noLabel, yesLabel) == True


def Progress(line1 = '', line2 = '', line3 = '', hide = False):
    dp = xbmcgui.DialogProgress()
    dp.create(TITLE, line1, line2, line3)
    dp.update(0)

    if hide:
        try:
            xbmc.sleep(250)
            WINDOW_PROGRESS = xbmcgui.Window(10101)
            CANCEL_BUTTON   = WINDOW_PROGRESS.getControl(10)
            CANCEL_BUTTON.setVisible(False)
        except:
            pass

    return dp


def DeleteFile(path):
    tries = 5
    while os.path.exists(path) and tries > 0:
        tries -= 1 
        try: 
            os.remove(path) 
            break 
        except: 
            xbmc.sleep(500)