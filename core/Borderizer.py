# Module:      core.Borderizer.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------
""" Defines a Borderizer object to add pixel borders to a krita node. """
from krita              import Selection , Krita , ManagedColor
from collections        import deque
from struct             import pack , unpack
from PyQt5.QtCore       import QRect

from .AlphaGrow         import Grow
from .AlphaScrapperSafe import Scrapper
from .FrameHandler      import FrameHandler
from .AlphaWriter       import Writer

# TODO: Do more flexible the gui:
# Support-multi config:
# main border config , secondary border config :: Integral a => (LineConfig ,SplitIndex a)
# where data LineConfig      = { thickness :: Integral a => a , method :: Integral a => a , color :: String }
#       newtype SplitIndex a = SplitIndex a

# TODO: Change available methods. Square, Round, Square and Round since
"""
METHODS = { "classic"         : 0 ,
            "corners"         : 1 ,
            "classicTcorners" : 2 ,
            "cornersTclassic" : 3 ,
            "classic&corners" : 4 ,
            "corners&classic" : 5 }
            """

# TODO: ADD "threshold" attribute.
# TODO: ADD "animated" attribute.
"""
KEYS = {  "method"    , # Int in [0..5]
          "thickness" , # Int in [1..]
          "color"     , # Str in {"FG","BG","CS"}
          "name"      , # Str
          "has-extra" , # Bool
          "extra-arg" , # Int in [0..thickness]
          "start"     , # Int in [-1..0]
          "finish"    } # Int in [-1..0]
          """

INDEX_METHODS = ["force","any-neighbor","corners","not-corners"]

METHODS = { "force"        : Grow.force_grow        ,
            "any-neighbor" : Grow.any_neighbor_grow ,
            "corners"      : Grow.corners_grow      ,
            "not-corners"  : Grow.not_corners_grow  }

KEYS = {  "methoddsc" , # [(method,thickness)] where method is
          "colordsc"  , # ( color_type , components )
                        # where color_type = "FG" | "BG" , "CS"
                        #       components = [UInt]
          "trdesc"    , # Transparency descriptor = ( transparency_value , threshold )
          "node"      , # Krita Node
          "doc"       , # Krita Document
          "kis"       , # Krita Instance
          "animation" , # None if it hasn't animation. Else ( start , finish ) -> start , finish are Ints in [UInt]
          "name"      , # String
          }

DEPTHS = { "U8"  : ("B" , 2**8  - 1 ) ,
           "U16" : ("H" , 2**16 - 1 ) ,
           "F16" : ("e" , 1.0       ) ,
           "F32" : ("f" , 1.0       ) }

class BorderException( Exception ):
    def __init__( self , args ): super().__init__( args )

class Borderizer( object ):
    # TODO: Remove kis explicit dependence.
    def __init__( self , info = None ):
        self.info = info

    #@DEPRECATED. this method has been moved to Grow.difference_with( self , external )
    @ classmethod
    def applyXORBetween( cls , data1 , data2 , size ):
        """ apply XOR bitwise operator between two data.
            NOTE: They must have the same length. """
        return bytearray( data1[i] ^ data2[i] for i in range(size) )

    @staticmethod
    def __get_true_color__( managedcolor ):
        depth = managedcolor.colorDepth()
        cmps  = managedcolor.components()
        
        bsize = int(depth[1:])
        ncmps = len(cmps)
        color = bytearray()
        dtype , dmax = DEPTHS[depth]

        if depth[0] == "U":
            # TODO: Use a better representation
            cast = int
        else:
            cast = float

        for i in range(ncmps - 1):
            color += pack( dtype , cast(cmps[i] * dmax) )
        color += pack( dtype , 0 )
        """
        if dtype == DEPTHS["F16"][0]:
            view   = memoryview( color ).cast( 'B' )
            writer = lambda value : pack( dtype , value )
            for i in range(ncmps - 1):
                # Component = normalized_value * max_value
                writer[i*bsize] = cmps[i] * dmax
            writer.release()

        else:
            writer = memoryview( color ).cast( dtype )
            for i in range(ncmps - 1):
                # Component = normalized_value * max_value
                writer[i] = cmps[i] * dmax
            writer.release()
        """
        return color

    #DEPRECATED:
    @staticmethod
    def get_color( color_type , components , node ):
        if   color_type == "FG":
            mcolor = self.view.foregroundColor()
        elif color_type == "BG":
            mcolor = self.view.backgroundColor()
        else:
            mcolor = ManagedColor( node.colorModel() , node.colorDepth() , node.colorProfile() )
            mcolor.setComponents( components )
        color = Borderizer.__get_true_color__( mcolor )
        return (color,color)

    @staticmethod
    def fillWith( target , pxdata , bounds ):
        target.setPixelData( pxdata , bounds.x() , bounds.y() , bounds.width() , bounds.height() )

    @staticmethod
    def getMinMaxValuesFrom( node ):
        pattern , maxv = DEPTHS[ node.colorDepth() ]
        return ( pack( pattern , 0 ) , pack( pattern , maxv ) )

    @staticmethod
    def updateAlphaOf( pxdata , length , nchans , minval , maxval , newalpha ):
        # TODO: Delete this
        #print( f"px: {pxdata}, len {length}, skip: {nchans}, max: {maxval}, minval{minval} , new{newalpha}" , end = "" )
        chSize = len(maxval)
        skip   = nchans - 1
        offset = skip * chSize
        step   = offset + chSize
        for i in range( length ):
            index = step * i + offset
            pxdata[ index : index + chSize ] = maxval if newalpha[i] else minval
        # TODO: Delete this
        # print( f", NEW: {pxdata}" )
        return pxdata
    @staticmethod
    def makePxDataWithColor( colorbytes , repeat_times ):
        return colorbytes * repeat_times

    @staticmethod
    def applyMethodRecipe( grow , recipe ):
        """ Apply the grow recipe to the grow object. 
            grow :: Grow ; recipe :: [(String,Int)] """
        for task , times in recipe:
            for _ in range(times):
                task( grow )
        return grow


    def run( self , **data_from_gui ):
        """ data_from_gui -> dict(...)
                | datafrom_gui = { 'method' : ... , 'width' : ... , 'color' : ... , 'name' : ... , 'has-extra' : ... ,
                                   'extra-arg: ... } """

        if set(data_from_gui.keys()) != KEYS:
            print( f"[Borderizer] Couldn't match the input dict():\n{data_from_gui}, with the required keys: {KEYS}" )
            return False

        # [@] Initialization
        node = data_from_gui["node"]
        doc  = data_from_gui["doc"]
        kis  = data_from_gui["kis"]
        view = kis.activeWindow().activeView()

        # Method purify:
        methodRecipe = []
        thickness    = 0
        for mdesc in data_from_gui["methoddsc"]:
            methodRecipe.append( (METHODS[ mdesc[0] ] , mdesc[1]) )
            thickness += mdesc[1]

        # Color selection:
        colorType , components = data_from_gui["colordsc"]
        if   colorType == "FG":
            mcolor = view.foregroundColor()
        elif colorType == "BG":
            mcolor = view.backgroundColor()
        else:
            # TODO: extract
            mcolor = ManagedColor( node.colorModel() , node.colorDepth() , node.colorProfile() )
            mcolor.setComponents( components )
        color  = Borderizer.__get_true_color__( mcolor )

        # Bounds selection:
        nbounds     = node.bounds()
        if nbounds.isEmpty():
            print( f"[Borderizer] The layer is empty." )
            return False


        dbounds     = doc.bounds()
        # Try to get natural bounds:
        protoBounds = QRect( nbounds.x()      - thickness   ,
                             nbounds.y()      - thickness   ,
                             nbounds.width()  + 2*thickness ,
                             nbounds.height() + 2*thickness )
        if dbounds.contains( protoBounds ):
            bounds = protoBounds
        else:
            bounds = dbounds

        # Misc & Time:
        name          = data_from_gui["name"]
        transparency , threshold = data_from_gui["trdesc"]

        # They're used for the writing proccess
        TRANSPARENT , OPAQUE = Borderizer.getMinMaxValuesFrom( node )

        batchK , batchD = kis.batchmode() , doc.batchmode()
        kis.setBatchmode( True )
        doc.setBatchmode( True )

        # [!] Run method:
        width  = bounds.width()
        chans  = node.channels()
        nchans = len(chans)

        # How many elements and their true size in the node.
        length = bounds.width() * bounds.height()
        pxSize = length * nchans

        source = node
        target = doc.createNode( ".target" , "paintlayer" )
        # Link the target with the document: (Just above the node)
        source.parentNode().addChildNode( target , source )

        # First Abstractions
        scrap  = Scrapper()
        frameH = FrameHandler( doc , kis )
        # Builds the color data
        colordata = Borderizer.makePxDataWithColor( color , length )

        # Time Selection:
        protoTimeline = data_from_gui["animation"]
        if protoTimeline:
            start , finish = protoTimeline
            timeline       = frameH.get_animation_range( source , start , finish + 1 )
        else:
            timeline       = None
        
        # Decide if apply a single step or multiple steps (for animated nodes)
        if timeline:
            grow = Grow.singleton()
            frameH.build_directory()
            for t in timeline:
                # Update the current time and wait in synchronous mode
                doc.setCurrentTime(t)
                doc.refreshProjection()
                doc.waitForDone()

                alpha  = scrap.extractAlpha( source , bounds , transparency , threshold )
                grow.setData( alpha , width , length , safe_mode = True )
                # Make the borders and update the target data.
                Borderizer.applyMethodRecipe( grow , methodRecipe )
                newAlpha = grow.difference_with( alpha )
                # Update and Write
                Borderizer.updateAlphaOf( colordata , length , nchans , TRANSPARENT , OPAQUE , newAlpha )
                Borderizer.fillWith( target , colordata , bounds )

                # TODO: Verify if this is totally required here
                doc.refreshProjection()
                doc.waitForDone()

                # TODO: Make this more general
                frameH.exportFrame( f"frame{t:05}.png" , target )

            # Exit:
            frameH.importFrames( start )
            border = doc.topLevelNodes()[0]
            border.setName( name )

            # Explicit Cleaning:
            target.remove()
            del target
            done = True
        else:
            alpha    = scrap.extractAlpha( source , bounds , transparency , threshold )
            grow     = Grow( alpha , width , length , safe_mode = True )
            Borderizer.applyMethodRecipe( grow , methodRecipe )
            newAlpha = grow.difference_with( alpha )
            # Update and Write
            Borderizer.updateAlphaOf( colordata , length , nchans , TRANSPARENT , OPAQUE , newAlpha )
            Borderizer.fillWith( target , colordata , bounds )

            # Exit:
            border = target
            border.setName( name )

            done = True

        doc.refreshProjection()
        kis.setBatchmode( batchK )
        doc.setBatchmode( batchD )
        return done

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

    #@DEPRECATED.
    @classmethod
    def classic( cls , alpha , grow , config ):
        return grow.repeated_classic_grow( alpha , repeat = config["thickness"] )

    #@DEPRECATED.
    @classmethod
    def corners( cls , alpha , grow_object , config ):
        return grow.repeated_corners_grow( alpha , repeat = config["thickness"] )

    #@DEPRECATED.
    @classmethod
    def classic_then_corners( cls , alpha , grow , config ):
        """ apply classic into [0..splitIndex-1] then
            apply corners into [splitIndex..length] """
        rem     = config["thickness"] - config["split-index"] + 1
        partial = grow.repeated_classic_grow( alpha   , repeat = config["split-index"] )
        total   = grow.repeated_corners_grow( partial , repeat = rem )
        return total

    #@DEPRECATED.
    @classmethod
    def corners_then_classic( cls , alpha , grow , config ):
        """ apply corners into [0..splitIndex-1] then
            apply classic into [splitIndex..length] """
        rem     = config["thickness"] - config["split-index"] + 1
        partial = grow.repeated_corners_grow( alpha   , repeat = config["split-index"] )
        total   = grow.repeated_classic_grow( partial , repeat = rem )
        return total

    #@DEPRECATED.
    @classmethod
    def corners_and_classic( cls , alpha , grow , config ):
        partial = alpha
        rem     = config["thickness"] - config["split-index"] + 1
        for i in range(config["split-index"]):
            partial = grow.corners_grow( partial )
        for i in range(rem):
            total   = grow.classic_grow( total   )
        return total

    #@DEPRECATED.
    @classmethod
    def classic_and_corners( cls , alpha , grow , config ):
        partial = alpha
        rem     = config["thickness"] - config["split-index"] + 1
        for i in range(config["split-index"]):
            partial = grow.classic_grow( partial )
        for i in range(rem):                              # This means we have to handle manually the data consistency
            total   = grow.corners_grow( total   )
        return total


    @staticmethod
    def getTrueColorFrom( managedcolor ):
        """ Includes Alpha """
        pattern = DEPTH[managedcolor.colorDepth()]
        cmps    = managedcolor.components()
        cmpsize = pattern

        if pattern == DEPTH["F16"]:
            pass
        else:
            pass
            
        for c in managedcolor.components():
            pass
        return bytearray()
    # TODO: Change this by:
    # makeBorders( cls , **kwargs )

    @classmethod
    def makeBorders( cls , **task_info ):
        # Be careful with data consistency
        safety = True
        # TODO: Remove some redundant information in task_info as task_info["doc"]
        # [Common Variables] -------------------------------------
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

        # [Abstract Services] -------------------------------------
        scrap = Scrapper()                          # No more info needed
        write = Writer()

        # This must be only width() and height()
        # size  = scrap.channelSize(source) * bounds.width() * bounds.height()
        size  = bounds.width() * bounds.height()
        full_size = size * scrap.channelNumber(source) * scrap.channelSize(source)

        #grow   = Grow( size , width , safety )       # Needs: size , width , mode
        framIO = FrameHandler( doc , kis )  # Needs: node , doc , kis , name , xRes , yRes , infoObject

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
            grow = Grow( alpha , width , size , safety )
            # -- Grow Data --
            for _ in range(config["thickness"]):
                grow.any_neighbor_grow()
            new_alpha = grow.difference_with( alpha )
            #extra = method( extra , grow , config )

            # -- Difference & Lift to Context --
            # TODO: Change this for a better method
            #TALPHA.setPixelData( Borderizer.applyXORBetween(extra,alpha,size) , bounds )
            write.writeAlpha( target , new_alpha , full_size , bounds )

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
