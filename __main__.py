# Module:      __main__.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ----------------------------------------------
"""
    package's main module. It's used for test the GUI outside
    Krita.
    >>> $ python3 -m pixel-borders

    With krita runner (on Linux)
    >>> $ export PYTHONPATH=$HOME/.local/share/krita/pykrita/
    >>> $ cd $HOME/.local/share/krita/pykrita/
    >>> $ kritarunner -s pixel_borders.__main__ -f main
    (kritarunner -s script-name -f function-name)
"""
from .SetupGUI import main
main()
