# Module:      __main__.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ----------------------------------------------
"""
    Package used to run the Pixel Border Plugin as a python
    module outside Krita.

    Doing GUI testing in bash (on Linux):
    >>> $ cd $HOME/.local/share/krita/pykrita/
    >>> $ python3 -m pixel_borders

    Douing GUI testing with kritarunner (on Linux)
    >>> $ export PYTHONPATH=$HOME/.local/share/krita/pykrita/
    >>> $ cd $HOME/.local/share/krita/pykrita/
    >>> $ kritarunner -s pixel_borders.__main__
    (kritarunner -s script-name -f function-name)
"""
from .SetupGUI import main
main()
