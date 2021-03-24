# Module:   DataLoader.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# ---------------------------------------------
"""
    Module used to load and write recipe files.

    [:] Defined in this module
    --------------------------
    loadData    :: func( str , bool ) -> IO ()
        load data from pixel_borders/previous.json

    writeData   :: func( str , bool ) -> IO ()
        writes data into pixel_borders/previous.json

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""

import os
import json
import sys

CURRENT_DIRECTORY = os.path.dirname( os.path.abspath(__file__) )
DEFAULT_FILENAME  = "previous.json"
def loadData( filename = DEFAULT_FILENAME , debug = False ):
    """ load data from pixel_borders/previous.json """

    path = f"{CURRENT_DIRECTORY}/{filename}"
    try:
        with open( path  , 'r' ) as handle:
            data = json.load( handle )
        if debug: print( f"[Pixel Border Extension]: Data loaded successfully." , file = sys.stderr )
    except Exception as err:
        if debug: print( f"[Pixel Border Extension]: Unable to find {path} ; err = {err.args}" , file = sys.stderr )
        data = {}
    return data

def writeData( data = {} , filename = DEFAULT_FILENAME , debug = False ):
    """ writes data into pixel_borders/previous.json """

    path = f"{CURRENT_DIRECTORY}/{filename}"
    try:
        with open( path , 'w' ) as handle:
            json.dump( data , handle , indent = 4 )
        if debug: print( f"[Pixel Border Extension]: Data saved into {path}" , file = sys.stderr )
        return True
    except Exception as err:
        if debug: print( f"[Pixel Border Extension]: Unable to save the current data into {path} ; err = {err.args}" , file = sys.stderr )
        return False
