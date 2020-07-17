from AlphaGrow     import Grow
from AlphaScrapper import Scrapper

class Borderizer( object ):
    def __init__( self , node , doc ):
        self.node   = node
        self.bounds = doc.bounds()

    def __run__( self , node , doc ):
        s    = Scrapper()
        w    = doc.bounds().width()
        data = s.extract_alpha( node , doc  )
        g    = Grow( data , w , True ) # True ==> Secure mode
        
