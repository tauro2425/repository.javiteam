# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta
# XBMC entry point
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

# Constants
__plugin__  = "pelisalacarta"
__author__  = "pelisalacarta"
__url__     = "http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/"
__date__ = "26/03/2015"
__version__ = "4.0"

import os
import sys
from core import config
from core import logger

logger.info("pelisalacarta.default init...")

librerias = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'lib' ) )
sys.path.append (librerias)

from platformcode import launcher

if sys.argv[1] == "1":
    # Esto solo se ejecuta la primera vez que entramos en el plugin
    launcher.start()

launcher.run()