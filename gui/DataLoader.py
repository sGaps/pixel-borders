from PyQt5.QtWidgets import QPushButton
from os              import path
import json
import sys
 
this_module_dir = path.dirname( path.abspath(__file__) )
class DataLoader( QPushButton ):
    DEFAULT_FILE = "data.json"
    PATH         = f"{this_module_dir}/{DEFAULT_FILE}"
    NAME         = "Load previous data"
    def __init__( self , parent = None ):
        super().__init__( DataLoader.NAME , parent = parent )
        self.released.connect( self.loadData )

    def loadData( self , keys = None ):
        try:
            jsonFile = open( DataLoader.PATH , 'r' )
            data     = json.load( jsonFile )
            if keys:
                data = data if keys == set( data.keys() ) else None
        except:
            data     = None
        return data

    def writeData( self , data , keys = None ):
        if not data and keys and keys != set( data.keys() ):
            return False

        normalExit = False
        try:
            jsonFile = open( DataLoader.PATH , 'w' )
            json.dump( data , jsonFile , indent = 4 )
            normalExit = True
        except:
            print( f"[DATA LOADER]: Couldn't Write data into {DataLoader.PATH}" , file = sys.stderr )
        return normalExit
