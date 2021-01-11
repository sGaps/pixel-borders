"""
    Utility module to load and write configuration files.

    [:] Defined in this module
    --------------------------
    loadData    :: function
    writeData   :: function

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""

import os
import json
import sys

CURRENT_DIRECTORY = os.path.dirname( os.path.abspath(__file__) )
DEFAULT_FILENAME  = "previous.json"
def loadData( filename = DEFAULT_FILENAME , debug = False ):
    path = f"{CURRENT_DIRECTORY}/{filename}"
    try:
        with open( f"{path}" , 'r' ) as handle:
            data = json.load( handle )
        if debug: print( f"[Pixel Border Extension]: Data loaded successfully." , file = sys.stderr )
    except Exception as err:
        if debug: print( f"[Pixel Border Extension]: Unable to find {path} ; err = {err.args}" , file = sys.stderr )
        data = {}
    return data

def writeData( data = {} , filename = DEFAULT_FILENAME , debug = False ):
    path = f"{CURRENT_DIRECTORY}/{filename}"
    try:
        with open( filename , 'w' ) as handle:
            json.dump( data , handle , indent = 4 )
        if debug: print( f"[Pixel Border Extension]: data saved into {path}" , file = sys.stderr )
        return True
    except Exception as err:
        if debug: print( f"[Pixel Border Extension]: Unable to save the current data into {path} ; err = {err.args}" , file = sys.stderr )
        return False

