# Module:      gui.KisLookup.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------------------
"""
    Utility module for manage and test the GUI inside and outside krita.

    [:] Defined in this module
    --------------------------
    KRITA_AVAILABLE :: bool
        says when krita's function can be used.

    debug           :: bool
        when it's true, prints in stderr when krita is or not loaded.

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""
from sys import stderr
debug  = False
dprint = (lambda s : print( s , file = stderr )) if debug else (lambda s : ())
try:
    import krita
    KRITA_AVAILABLE = True
except:
    kis             = None
    krita           = None
    KRITA_AVAILABLE = False
    dprint( f"[KRITA - LOOKUP] not available." )
else:
    kis = krita.Krita.instance()
    dprint( f"[KRITA - LOOKUP] available." )
    dprint( f"[KRITA - LOOKUP]:\n\tkrita -> {kis}" )
