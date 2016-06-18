# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Sean Poyser and Richard Dean (write2dixie@gmail.com)
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with XBMC; see the file COPYING. If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# http://www.gnu.org/copyleft/gpl.html
#

import os
import xbmc
import xbmcgui
import xbmcaddon

def deleteDB():
    try:
        xbmc.log("[TVGuia JAVI-TEAM] Borrando Base de Datos...", xbmc.LOGDEBUG)
        dbPath = xbmc.translatePath(xbmcaddon.Addon(id = 'script.ftvguide').getAddonInfo('profile'))
        dbPath = os.path.join(dbPath, 'source.db')

        delete_file(dbPath)

        passed = not os.path.exists(dbPath)

        if passed:
            xbmc.log("[TVGuia JAVI-TEAM] Borrando base de Datos...Espere", xbmc.LOGDEBUG)
        else:
            xbmc.log("[TVGuia JAVI-TEAM] Borrando base de Datos...fallido", xbmc.LOGDEBUG)

        return passed

    except Exception, e:
        xbmc.log('[TVGuia JAVI-TEAM] Borrando base de Datos...Excepcion', xbmc.LOGDEBUG)
        return False

def delete_file(filename):
    tries = 10
    while os.path.exists(filename) and tries > 0:
        try:
            os.remove(filename)
            break
        except:
            tries -= 1

if __name__ == '__main__':
    if deleteDB():
        d = xbmcgui.Dialog()
        d.ok('Javi.Team Guide', '[COLOR yellow]La base de datos ha sido borrada[/COLOR]', '[COLOR yellow]Se vuelve a crear la próxima vez que inicie la guía[/COLOR]')
    else:
        d = xbmcgui.Dialog()
        d.ok('Javi.Team Guide', '[COLOR red]Fallo al borrar base de datos[/COLOR]', '[COLOR red]base de datos bloqueada[/COLOR]', '[COLOR red]Reinicie kodi de nuevo[/COLOR]')
		
import os
import xbmc
import xbmcgui
import xbmcaddon

def deleteDB():
    try:
        xbmc.log("[TVGuia JAVI-TEAM] Borrando Base de Datos...", xbmc.LOGDEBUG)
        dbPath = xbmc.translatePath(xbmcaddon.Addon(id = 'script.ftvguide').getAddonInfo('profile'))
        dbPath = os.path.join(dbPath, 'addons.ini')

        delete_file(dbPath)

        passed = not os.path.exists(dbPath)

        if passed:
            xbmc.log("[TVGuia JAVI-TEAM] Borrando base de CANALES...Espere", xbmc.LOGDEBUG)
        else:
            xbmc.log("[TVGuia JAVI-TEAM] Borrando base de CANALES...fallido", xbmc.LOGDEBUG)

        return passed

    except Exception, e:
        xbmc.log('[TVGuia JAVI-TEAM] Borrando base de CANALES...Excepcion', xbmc.LOGDEBUG)
        return False

def delete_file(filename):
    tries = 10
    while os.path.exists(filename) and tries > 0:
        try:
            os.remove(filename)
            break
        except:
            tries -= 1

if __name__ == '__main__':
    if deleteDB():
        d = xbmcgui.Dialog()
        d.ok('Javi.Team Guide', '[COLOR yellow]La base de CANALES ha sido borrada[/COLOR]', '[COLOR yellow]Se vuelve a crear la próxima vez que inicie la guía[/COLOR]')
    else:
        d = xbmcgui.Dialog()
        d.ok('Javi.Team Guide', '[COLOR red]Fallo al borrar base de CANALES[/COLOR]', '[COLOR red]base de CANALES bloqueada[/COLOR]', '[COLOR red]Reinicie kodi de nuevo[/COLOR]')

import os
import xbmc
import xbmcgui
import xbmcaddon

def deleteDB():
    try:
        xbmc.log("[TVGuia JAVI-TEAM] Borrando Base de Datos...", xbmc.LOGDEBUG)
        dbPath = xbmc.translatePath(xbmcaddon.Addon(id = 'script.ftvguide').getAddonInfo('profile'))
        dbPath = os.path.join(dbPath, 'guide.xmltv')

        delete_file(dbPath)

        passed = not os.path.exists(dbPath)

        if passed:
            xbmc.log("[TVGuia JAVI-TEAM] Borrando base de EPG...Espere", xbmc.LOGDEBUG)
        else:
            xbmc.log("[TVGuia JAVI-TEAM] Borrando base de EPG...fallido", xbmc.LOGDEBUG)

        return passed

    except Exception, e:
        xbmc.log('[TVGuia JAVI-TEAM] Borrando base de EPG...Excepcion', xbmc.LOGDEBUG)
        return False

def delete_file(filename):
    tries = 10
    while os.path.exists(filename) and tries > 0:
        try:
            os.remove(filename)
            break
        except:
            tries -= 1

if __name__ == '__main__':
    if deleteDB():
        d = xbmcgui.Dialog()
        d.ok('Javi.Team Guide', '[COLOR yellow]La base de EPG ha sido borrada[/COLOR]', '[COLOR yellow]Se vuelve a crear la próxima vez que inicie la guía[/COLOR]')
    else:
        d = xbmcgui.Dialog()
        d.ok('Javi.Team Guide', '[COLOR red]Fallo al borrar base de EPG', '[COLOR red]base de EPG bloqueada', '[COLOR red]Reinicie kodi de nuevo[/COLOR]')		

