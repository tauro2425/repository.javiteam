import sys, traceback

###################################################################### DMO ######################################################################
import requests
import xbmcgui

mi_version = ["2200016","06","15"]

r = requests.get("https://www.cubbyusercontent.com/pl/version.txt/_5ab61c39fc5143389fb58f0a8fe2b029")
data = r.content

ult_version = data.split(".")

hay_nueva = False
if mi_version[0] < ult_version[0]:
	hay_nueva = True
else:
	if mi_version[1] < ult_version[1]:
		hay_nueva = True
	else:
		if mi_version[2] < ult_version[2]:
			hay_nueva = True
			
if hay_nueva == True:
	titu = "ATENCION!!!!"
	lin1 = "         Version [COLOR red]OBSOLETA de SportsDevil[/COLOR] updated by DMO"
	lin2 = " Ya tienes disponible la ultima version para poder actualizarlo"
	lin3 = "[COLOR yellow]Descarga:[/COLOR] [COLOR red][B]http://bit.do/UltSpD[/COLOR][/B]    ...Ojo con las Mayusculas!!"
	xbmcgui.Dialog().ok(titu, lin1, lin2, lin3)
###################################################################### DMO ######################################################################




# REMOTE DEBUGGING
REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True, suspend=False)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)
    except:
        sys.stderr.write('Remote Debugger is not started')




# ACTUAL ADDON
from lib import main

try:
    myAddon = main.Main()
    myAddon.run(sys.argv)
except:
    traceback.print_exc(file = sys.stdout)