from AlphaGrow import Grow
class Selector( object ):
    def __init__( self , node , doc ):
        self.node   = node
        self.bounds = doc.bounds()
