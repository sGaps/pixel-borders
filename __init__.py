# Gaps / sGaps / ArtGaps | Language Python
from sys import stderr
try:
    from krita import Krita
    from .main import PixelExtension
except ImportError as error:
    from .main import PixelExtension
    for e in error.args:
        print( "[Pixel Border] Warning:" , e , file = stderr )
else:
    print( "[Pixel Border] Loaded Package" , file = stderr )
    pass
    # [!] Initialize The extension:
    kis = Krita.instance()
    ext = PixelExtension( parent = kis )

    Scripter.addExtension( ext )    # Scripter is defined in the global krita's dictionary
