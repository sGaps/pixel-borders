# Module:      gui.krita_connection.Lookup.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------------------
from sys import stderr
debug  = False
dprint = (lambda s : print( s , file = stderr )) if debug else (lambda s : ())
try:
    import krita
    KRITA_AVAILABLE = True
except:
    KRITA_AVAILABLE = False
    dprint( f"[KRITA - LOOKUP] not available." )
else:
    kis = krita.Krita.instance()
    dprint( f"[KRITA - LOOKUP] available." )
    dprint( f"[KRITA - LOOKUP]:\n\tkrita -> {kis}" )
