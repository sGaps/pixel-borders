# Module:      core.Borderizer.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------
""" Defines a Borderizer object to add pixel borders to a krita node. """
from krita              import Selection , Krita
from collections        import deque

from .AlphaGrow         import Grow
from .AlphaScrapperSafe import Scrapper
from .FrameHandler      import FrameHandler
from .AlphaWriter       import Writer


METHODS = { "classic"         : 0 ,
            "corners"         : 1 ,
            "classicTcorners" : 2 ,
            "cornersTclassic" : 3 ,
            "classic&corners" : 4 ,
            "corners&classic" : 5 }

# ADD "threshold" attribute to this set
KEYS = { "method"     , # Int in [0..5]
          "thickness" , # Int in [1..]
          "color"     , # Str in {"FG","BG","CS"}
          "name"      , # Str
          "has-extra" , # Bool
          "extra-arg" , # Int in [0..thickness]
          "start"     , # Int in [-1..0]
          "finish"    } # Int in [-1..0]

class Borderizer( object ):
    def __init__( self , krita_instance , info = None ):
        self.kis   = krita_instance
        self.win   = self.kis.activeWindow()
        self.doc   = self.kis.activeDocument()
        #self.node  = self.doc.activeNode()
        self.view  = self.win.activeView()
        self.canvas = self.view.canvas()

    @classmethod
    def applyXORBetween( cls , data1 , data2 , size ):
        """ apply XOR bitwise operator between two data.
            NOTE: They must have the same length. """
        return bytearray( data1[i] ^ data2[i] for i in range(size) )

    def run( self , **data_from_gui ):
        """ data_from_gui -> dict(...)
                | datafrom_gui = { 'method' : ... , 'width' : ... , 'color' : ... , 'name' : ... , 'has-extra' : ... ,
                                   'extra-arg: ... } """

        if set(data_from_gui.keys()) != KEYS:
            return False
        passed_info = dict(data_from_gui)
    
        # Color selection:
        if   data_from_gui["color"] == "FG":
            passed_info["color"] = self.view.foregroundColor()
        elif data_from_gui["color"] == "BG":
            passed_info["color"] = self.view.backgroundColor()
        else:
            # This must build a Custom Managed Color
            passed_info["color"] = None
        m = data_from_gui["method"]
        if   m == 0: passed_info["method"] = Borderizer.classic
        elif m == 1: passed_info["method"] = Borderizer.corners
        elif m == 2: passed_info["method"] = Borderizer.classic_then_corners
        elif m == 3: passed_info["method"] = Borderizer.corners_then_classic
        elif m == 4: passed_info["method"] = Borderizer.classic_and_corners
        elif m == 5: passed_info["method"] = Borderizer.corners_and_classic

        passed_info["doc"]    = self.doc
        passed_info["kis"]    = self.kis
        passed_info["node"]   = self.doc.activeNode()
        passed_info["bounds"] = self.doc.bounds()

        return Borderizer.makeBorders( **passed_info )

    @classmethod
    def liftToChannel( cls , data , bounds , channel ):
        channel.setPixelData( data , bounds )

    # TODO: Finish this using Writer() and Writer.colorize()
    @classmethod
    def colorize( cls , node , color , size , bounds ):
        node.setPixelData( b"\x00" * size  ,
                           bounds.x()      , 
                           bounds.y()      , 
                           bounds.width()  , 
                           bounds.height() )

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
        for i in range(rem):                              # This means we have to handle manually the data consistency
            total   = grow.corners_grow( total   )
        return total

    # TODO: Change this by:
    # makeBorders( cls , **kwargs )
    @classmethod
    def makeBorders( cls , **task_info ):
        # Be careful with data consistency
        safety = False
        # TODO: Remove some redundant information in task_info as task_info["doc"]
        kis    = task_info["kis"]
        doc    = kis.activeDocument()
        win    = kis.activeWindow()
        view   = win.activeView()
        canvas = view.canvas()
        source = doc.activeNode()
        bounds = doc.bounds()
        width  = bounds.width()
        color  = task_info["color"]
        start  = task_info["start"]
        finish = task_info["finish"]
        method = task_info["method"]
        name   = task_info["name"]
        config = { "thickness"  : task_info["thickness"]  ,
                   "split-index" : task_info["extra-arg"] }

        scrap = Scrapper()                          # No more info needed
        write = Writer()
        # This must be only width() and height()
        # size  = scrap.channelSize(source) * bounds.width() * bounds.height()
        size  = bounds.width() * bounds.height()
        full_size = size * scrap.channelNumber(source) * scrap.channelSize(source)

        grow   = Grow( size , width , safety )       # Needs: size , width , mode
        framIO = FrameHandler( source , doc , kis )  # Needs: node , doc , kis , name , xRes , yRes , infoObject

        # Insert color in the border auxiliar layer
        target = doc.createNode( ".target" , "paintlayer" )
        Borderizer.colorize( target , color , full_size , bounds )

        chans  = source.channels()
        TALPHA = target.channels()[-1]      # Target's alpha

        timeline    = framIO.get_animation_range( source , start , finish + 1 )
        # TODO: Finish
        if not timeline:
            # -- Extract Alpha --
            alpha = scrap.extractAlpha( source , bounds , transparent = 0x00 , threshold = 0 )

            # -- Grow Data --
            extra = alpha.copy()
            extra = method( extra , grow , config )

            # -- Difference & Lift to Context --
            # TODO: Change this for a better method
            #TALPHA.setPixelData( Borderizer.applyXORBetween(extra,alpha,size) , bounds )
            write.writeAlpha( target , Borderizer.applyXORBetween(extra,alpha,size) , full_size , bounds )

            # -- End phase --
            border = target
            source.parentNode().addChildNode( border , source )
            border.setName( name )
            border.setColorLabel( source.colorLabel() )
            doc.refreshProjection()
            done = True

        else:
            # TODO: Fix problems with framehandler
            base_name = "frame"
            nframes   = len(timeline.stop-1)

            source.parentNode().addChildNode( target , source )
            if not framIO.build_directory():
                raise Exception( "Unable to write Output dir" )

            for t in timeline:
                # -- Update time --
                doc.setCurrentTime(t)
                # TODO: Verify if this is totally required.
                doc.refreshProjection()

                # -- Extract Alpha --
                alpha = scrap.extractAlpha( source , bounds , transparent = 0x00 , threshold = 0 )

                # -- Grow Data --
                extra = alpha.copy()
                extra = method( extra , grow , config )

                # -- Difference & Lift to Context --
                # TODO: Change this for a better method
                TALPHA.setPixelData( Borderizer.applyXORBetween(extra,alpha,size) , bounds )

                # -- Export --
                # TODO: Make this genereal form:
                framIO.exportFrame( f"{base_name}_{t:0{nframes}}" , target )

            # -- Import --
            done = framIO.importFrames( start )
            if not done:
                print( "[BORDERIZER] Unable to import files." , file = stderr )

            # -- New Node handle --
            border = doc.topLevelNodes()[0] # TODO: Verify if this is right.
            border.setName( name )
            doc.refreshProjection()

            # -- Clean up --
            target.remove() # Be careful with this
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
