from krita       import Selection , Krita
from collections import deque
# append , appendLeft , pop , popLeft

# TODO: DELETE THIS BLOCK [BEGIN]
if __name__ == "__main__":
    import sys
    import os
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser( __file__ ))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
    from core.AlphaGrow     import Grow
    from core.AlphaScrapper import Scrapper
    from core.FrameHandler  import FrameHandler
# TODO: DELETE THIS BLOCK [END]
else:
# TODO: De-Ident & delete else statement
    from .AlphaGrow     import Grow
    from .AlphaScrapper import Scrapper
    from .FrameHandler  import FrameHandler


METHODS = { "classic"         : 0 ,
            "corners"         : 1 ,
            "classicTcorners" : 2 ,
            "cornersTclassic" : 3 ,
            "classic&corners" : 4 ,
            "corners&classic" : 5 }
KEYS = { "method"     ,
          "width"     ,
          "color"     ,
          "name"      ,
          "has-extra" ,
          "extra-arg" }

class Borderizer( object ):
    def __init__( self , krita_instance , info = None ):
        self.kis   = krita_instance
        seff.win   = self.kis.activeWindow()
        self.doc   = self.kis.activeDocument()
        self.node  = self.doc.activeNode()
        self.view  = self.win.activeView()
        self.canvas = self.view.canvas()

    @classmethod
    def applyXORBetween( cls , data1 , data2 , size ):
        """ apply XOR bitwise operator between two data.
            NOTE: They must have the same length. """
        return bytearray( self.data1[i] ^ data2[i] for i in range(size) )

    def run( self , data_from_gui ):
        """ data_from_gui -> dict(...)
                | datafrom_gui = { 'method' : ... , 'width' : ... , 'color' : ... , 'name' : ... , 'has-extra' : ... ,
                                   'extra-arg: ... } """
        if set(data_from_gui.keys()) != KEYS:
            return False
    
        # Here, we have manage everything related to the worker method input:
        info = dict()

        # Color
        if   data_from_gui["color"] == "FG":
            info["color"] = self.view.foregroundColor()
        elif data_from_gui["color"] == "BG":
            info["color"] = self.view.backgroundColor()
        else:
            info["color"] = None

        
        info["bounds"] = self.doc.bounds()
        info["node"]   = self.node
        info["doc"]    = self.doc
        info["kis"]    = self.kis

        # TODO: Connect with data
        info["start"]  = self.doc.fullClipRangeStartTime()
        info["finish"] = self.doc.fullClipRangeEndTime()

        return self.makeBorders( info , general_info , )
        # Else, perform actions

    @classmethod
    def liftToChannel( cls , data , bounds , channel ):
        channel.setPixelData( data , bounds )

    @classmethod
    def colorize( cls , node , color , size , bounds ):
        channels = node
        parts    = color.components()
        for c in range( len(chans) - 1 ):
            # See how I can colorize this.
            channels[c].setPixelData( bytes(parts[c])*size , bounds  )

    @classmethod
    def classic( cls , alpha , grow , config ):
        return grow.repeated_classic_grow( alpha , repeat = config["thickness"] )

    @classmethod
    def corners( cls , alpha , grow_object , config ):
        return grow.repeated_corners_grow( alpha , repeat = config["thickness"] )

    @classmethod
    def classic_then_corners( cls , alpha , grow , config ):
        """ apply classic into [0..splitIndex-1] then
            apply corners into [splitIndex..length] """
        rem     = config["thickness"] - config["split-index"] + 1
        partial = grow.repeated_classic_grow( alpha   , repeat = config["split-index"] )
        total   = grow.repeated_corners_grow( partial , repeat = rem )
        return total

    @classmethod
    def corners_then_classic( cls , alpha , grow , config ):
        """ apply corners into [0..splitIndex-1] then
            apply classic into [splitIndex..length] """
        rem     = config["thickness"] - config["split-index"] + 1
        partial = grow.repeated_corners_grow( alpha   , repeat = config["split-index"] )
        total   = grow.repeated_classic_grow( partial , repeat = rem )
        return total

    @classmethod
    def corners_and_classic( cls , alpha , grow , config ):
        partial = alpha
        rem     = config["thickness"] - config["split-index"] + 1
        for i in range(config["split-index"]):
            partial = grow.corners_grow( partial )
        for i in range(rem):
            total   = grow.classic_grow( total   )
        return total

    @classmethod
    def classic_and_corners( cls , alpha , grow , config ):
        partial = alpha
        rem     = config["thickness"] - config["split-index"] + 1
        for i in range(config["split-index"]):
            partial = grow.classic_grow( partial )
        for i in range(rem):
            total   = grow.corners_grow( total   )
        return total

    @classmethod
    def makeBorders( cls , general_info , method , config ):
        """
            method :: bytearray -> Grow -> IO (bytearray) 
            config :: dict
                | config = {'thickness' -> int , 'split-index' -> int }
            info   :: dict
                | same as data_from_gui in .run() method. """
        if set(data_from_gui.keys() != KEYS:
            return False

        # NOTE: This means we have to handle manually the data consistency
        safety = False                              # This means we have to handle manually the data consistency
        bounds = general_info["bounds"]
        source = info["node"]
        width  = bounds.width()
        color  = general_info["color"]
        start  = info["start"]
        finish = info["finish"]
        doc    = info["doc"]
        kis    = info["kis"]

        scrap = Scrapper()                          # No more info needed
        size  = scrap.sizeChannel(source) * bounds.width() * bounds.height()

        grow   = Grow( size , width , safety )       # Needs: size , width , mode
        framIO = FrameHandler( source , doc , kis )  # Needs: node , doc , kis , name , xRes , yRes , infoObject

        bounds = doc.bounds()
        target = doc.createNode( ".target" , "paintlayer" )
        self.colorize( target , color , size  , bounds )

        # TODO: Verify if everything works with this:
        chans  = source.channels()
        TALPHA = chans[-1]                  # Target's alpha

        timeline    = framIO.get_animation_range( node , start , finish )
        # TODO: Finish
        if not timeline:
            # -- Extract Alpha --
            alpha = scrap.extractAlpha( node , bounds , opaque = 0xFF , transparent = 0x00 )

            # -- Grow Data --
            extra = alpha.copy()
            extra = method( extra , grow , config )

            # -- Difference & Lift to Context --
            TALPHA.setPixelData( self.applyXORBetween(extra,alpha) , bounds )

            # -- End phase --
            border = target
            border.setName( "border" )
            done = True

        else:
            base_name = "frame"
            for t in timeline:
                # -- Update time --
                doc.setCurrentTime(t)
                # TODO: Verify if this is totally required.
                doc.refreshProjection()

                # -- Extract Alpha --
                alpha = scrap.extractAlpha( node , bounds , opaque = 0xFF , transparent = 0x00 )

                # -- Grow Data --
                extra = alpha.copy()
                extra = method( extra , grow , config )
                # -- Difference & Lift to Context --
                TALPHA.setPixelData( self.applyXORBetween(extra,alpha) , bounds )

                # -- Export --
                # TODO: Make this genereal form:
                framIO.exportFrame( f"{base_name}_{t:5}" , target )

            # -- Import --
            done = framIO.importFrames( start )

            # -- New Node handle --
            border = doc.topLevelNodes()[0] # TODO: Verify if this is right.
            border.setName( name )

            # -- Clean up --
            target.remove()
            del target
        return done

# ---------------------------
# TODO: DELETE THIS
if __name__ == "__main__":
    kis = Krita.instance()
    d = kis.activeDocument()
    w = kis.activeWindow()
    v = w.activeView()
    n = d.activeNode()
    print( n.channels() )
    b = Borderizer(n,d,v)
    print( b.nodeOrChildrenAreAnimated(n) )
# ----------------------------
