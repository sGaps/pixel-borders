# Gaps / sGaps / ArtGaps | Language Python
from sys import stderr
try:
    pass
    #from krita import Krita
    #from .main import PixelExtension
except ImportError as error:
    from .main import PixelExtension
    for e in error.args:
        print( "[PACKAGE] Warning:" , e , file = stderr )
else:
    print( "[INFO] Loaded Package" , file = stderr )
    pass
    # [!] Initialize The extension:
    #kis = Krita.instance()
    #ext = PixelExtension( parent = kis )

    #kis.addExtension     ( ext )
    #Scripter.addExtension( ext )
