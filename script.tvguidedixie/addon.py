#
#      Copyright (C) 2014 Sean Poyser and Richard Dean (write2dixie@gmail.com)
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
import urllib
import urllib2
from hashlib import md5
import socket
import os
import re
import shutil
import download
import extract
import update
import dixie
import getIni

import filmon
# filmon.initialise()


socket.setdefaulttimeout(10) # 10 seconds

import settings
settings.validate()


ADDON       = dixie.ADDON
HOME        = dixie.HOME
TITLE       = dixie.TITLE
VERSION     = dixie.VERSION
DIXIEURL    = dixie.DIXIEURL
DIXIELOGOS  = dixie.DIXIELOGOS
SKIN        = dixie.SKIN
SKINVERSION = dixie.SKINVERSION
INIVERSION  = dixie.INIVERSION

skin        = dixie.SKIN
addonpath   = dixie.RESOURCES
datapath    = dixie.PROFILE
extras      = os.path.join(datapath,   'extras')
logos       = os.path.join(extras,     'logos')
logofolder  = os.path.join(logos,      'None')
skinfolder  = os.path.join(extras,     'skins')
dest        = os.path.join(skinfolder, 'skins.zip')
default_ini = os.path.join(addonpath,  'addons.ini')
local_ini   = os.path.join(addonpath,  'local.ini')
current_ini = os.path.join(datapath,   'addons.ini')
database    = os.path.join(datapath,   'program.db')


def CheckVersion():
    prev = ADDON.getSetting('VERSION')
    curr = VERSION
    dixie.log('****** ONTAPP.TV %s LAUNCHED ******' % str(VERSION))

    if prev == curr:
        return

    dixie.SetSetting('VERSION', curr)

    d = xbmcgui.Dialog()
    d.ok(TITLE + ' - ' + VERSION, 'IMPORTANT. We have moved our payment gateway to www.stripe.com', 'When your subscription expires...', 'Please renew using your credit/debit card.')
    showChangelog()


def showChangelog(addonID=None):
    try:
        if addonID:
            ADDON = xbmcaddon.Addon(addonID)
        else:
            ADDON = xbmcaddon.Addon()

        f     = open(ADDON.getAddonInfo('changelog'))
        text  = f.read()
        title = '%s - %s' % (xbmc.getLocalizedString(24054), ADDON.getAddonInfo('name'))

        showText(title, text)

    except:
        pass


def showText(heading, text):
    id = 10147

    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)

    win = xbmcgui.Window(id)

    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass


def CheckForChannels():
    dir    = xbmc.translatePath(ADDON.getAddonInfo('profile'))
    folder = os.path.join(dir, 'channels')
    files  = []
    try:    current, dirs, files = os.walk(folder).next()
    except: pass
    if len(files) == 0:
        dixie.SetSetting('updated.channels', -1) # force refresh of channels


def CheckSkin():
    path = os.path.join(skinfolder, skin)
    curr = SKINVERSION

    if not os.path.exists(path):
        DownloadSkins()
        dixie.SetSetting('SKINVERSION', curr)


def CheckSkinVersion():
    prev = ADDON.getSetting('SKINVERSION')
    curr = SKINVERSION

    if not prev == curr:
        DownloadSkins()
        dixie.SetSetting('SKINVERSION', curr)


def CheckIniVersion():
    getIni.getIni()


def CheckFilmOn():
    getIni.ftvIni()


def CheckForUpdate():
    if xbmcgui.Window(10000).getProperty('OTT_UPDATING') != 'True':
        import update
        update.checkForUpdate(silent = True)
        return

    while xbmcgui.Window(10000).getProperty('OTT_UPDATING') == 'True':
        xbmc.sleep(1000)


def DownloadSkins():
    url  = dixie.GetExtraUrl() + 'resources/skins-12-01-2015.zip'

    try:
        os.makedirs(skinfolder)
    except:
        pass

    download.download(url, dest)
    extract.all(dest, extras)
    dixie.SetSetting('SKINVERSION', SKINVERSION)

    try:
        os.remove(dest)
    except:
        pass


def CopyKeymap():
    src = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'zOTT.xml')
    if os.path.exists(src):
        os.remove(src)

    src = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'super_favourites_menu.xml')

    if not os.path.exists(src):
        return

    dst = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), 'super_favourites_menu.xml')

    import shutil
    shutil.copyfile(src, dst)

    os.remove(src)

    xbmc.sleep(1000)
    xbmc.executebuiltin('Action(reloadkeymaps)')


def RemoveKeymap():
    src = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), 'super_favourites_menu.xml')

    if not os.path.exists(src):
        return

    dst = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'super_favourites_menu.xml')

    import shutil
    shutil.copyfile(src, dst)

    os.remove(src)

    xbmc.sleep(1000)
    xbmc.executebuiltin('Action(reloadkeymaps)')


try:
    path = os.path.join(datapath, 'tvgdinstall.txt')

    if not os.path.exists(path):
        url = dixie.GetExtraUrl() + 'resources/tvgdinstall.txt'
        urllib.urlretrieve(url, path)

    if not os.path.exists(current_ini):
        try: os.makedirs(datapath)
        except: pass
        shutil.copy(default_ini, datapath)
        shutil.copy(local_ini, datapath)        
except:
    pass


def main(doLogin=True):
    CheckSkin()
    busy = dixie.ShowBusy()

    import buggalo
    import gui

    buggalo.GMAIL_RECIPIENT = 'write2dixie@gmail.com'


    try:
        if not dixie.validToRun():
            dixie.notify('Failed to obtain a response from On-Tapp.TV')
            return

        CheckVersion()
        CheckSkinVersion()
        CheckIniVersion()
        CheckFilmOn()
        CheckForUpdate()
        CheckForChannels()

        dixie.log('****** OnTapp.TV - All OK *******')

        xbmcgui.Window(10000).setProperty('OTT_RUNNING', 'True')
        xbmc.executebuiltin('XBMC.ActivateWindow(home)')

        w = gui.TVGuide()

        if busy:
            busy.close()
            busy = None

        CopyKeymap()
        w.doModal()
        RemoveKeymap()
        del w

        xbmcgui.Window(10000).clearProperty('OTT_RUNNING')

    except Exception:
        buggalo.onExceptionRaised()


kodi = True
if xbmcgui.Window(10000).getProperty('OTT_KODI').lower() == 'false':
    kodi = False
xbmcgui.Window(10000).clearProperty('OTT_KODI')


main(kodi)

filmon.logout()