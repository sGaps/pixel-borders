# Module:      gui.krita_connection.Lookup.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------------------
from sys import stderr
debug  = True           # TODO: Change to False
dprint = (lambda s : print( s , file = stderr )) if debug else (lambda s : ())
try:
    import krita
    KRITA_AVAILABLE = True
except:
    KRITA_AVAILABLE = False
    dprint( f"[KRITA - LOOKUP] not available." )
else:
    dprint( f"[KRITA - LOOKUP] available." )
    kis = krita.Krita.instance()

    # TODO: Uncomment
    #doc = kis.activeDocument()
    # TODO: Remove
    #doc = kis.openDocument( "/home/sgaps/.local/share/krita/pykrita/pixel_border/test_gui/single.kra" )

    dprint( f"[KRITA - LOOKUP]:\n\tkrita -> {kis}" )

    # TODO: Uncomment
    #node = doc.activeNode()
    # TODO: Remove
    #node = doc.topLevelNodes()[1]
