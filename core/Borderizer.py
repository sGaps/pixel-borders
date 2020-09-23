# Module:      core.Borderizer.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------
""" Defines a Borderizer object to add pixel borders to a krita node. """
from krita              import Selection , Krita , ManagedColor
from struct             import pack , unpack
from PyQt5.QtCore       import QRect
from sys                import stderr
from collections        import deque

from .AlphaGrow         import Grow
from .AlphaScrapperSafe import Scrapper
from .FrameHandler      import FrameHandler


INDEX_METHODS = ["force","any-neighbor","corners","not-corners"]

METHODS = { "force"        : Grow.force_grow        ,
            "any-neighbor" : Grow.any_neighbor_grow ,
            "corners"      : Grow.corners_grow      ,
            "not-corners"  : Grow.not_corners_grow  }

# Keys used in the data structure passed by the GUI
KEYS = {  "methoddsc" , # [[method,thickness]] where method is
          "colordsc"  , # ( color_type , components )
                        # where color_type = "FG" | "BG" , "CS"
                        #       components = [UInt]
          "trdesc"    , # Transparency descriptor = ( transparency_value , threshold )
          # Are node , doc and kis really required?
          "node"      , # Krita Node
          "doc"       , # Krita Document
          "kis"       , # Krita Instance
          "animation" , # None if it hasn't animation. Else ( start , finish ) -> start , finish are Ints in [UInt]
          "name"      , # String
          }

# Support for krita color depths. Key -> ( Read_Write_Pattern , Max_Value )
DEPTHS = { "U8"  : ("B" , 2**8  - 1 ) ,
           "U16" : ("H" , 2**16 - 1 ) ,
           "F16" : ("e" , 1.0       ) ,
           "F32" : ("f" , 1.0       ) }

class BorderException( Exception ):
    def __init__( self , args ): super().__init__( args )

class Borderizer( object ):
    ANIMATION_IMPORT_DEFAULT_INDEX = -1
    def __init__( self , info = None , cleanUpAtFinish = False ):
        self.info = info
        self.cleanUpAtFinish = cleanUpAtFinish

    @staticmethod
    def __get_true_color__( managedcolor ):
        """ __get_true_color__ :: krita.ManagedColor -> bytearray 

            Takes a krita.ManagedColor and returns a physical representation of the color (as bytearray structure) """
        depth = managedcolor.colorDepth()
        cmps  = managedcolor.components()
        
        bsize = int(depth[1:])
        ncmps = len(cmps)
        color = bytearray()
        dtype , dmax = DEPTHS[depth]

        if depth[0] == "U":
            cast = int
        else:
            cast = float

        for i in range(ncmps - 1):
            color += pack( dtype , cast(cmps[i] * dmax) )
        color += pack( dtype , 0 )
        return color

    @staticmethod
    def fillWith( target , pxdata , bounds ):
        """ fillWith :: krita.Node -> bytearray -> PyQt5.QtCore.QRect -> IO () 
            Updates the node pixelData using a bytearray and a QRect """
        target.setPixelData( pxdata , bounds.x() , bounds.y() , bounds.width() , bounds.height() )

    @staticmethod
    def getMinMaxValuesFrom( node ):
        """ getMinMaxValuesFrom :: Node -> (Number,Number) """
        pattern , maxv = DEPTHS[ node.colorDepth() ]
        return ( pack( pattern , 0 ) , pack( pattern , maxv ) )

    @staticmethod
    def updateAlphaOf( pxdata , length , nchans , minval , maxval , newalpha ):
        chSize = len(maxval)
        skip   = nchans - 1
        offset = skip * chSize
        step   = offset + chSize
        for i in range( length ):
            index = step * i + offset
            pxdata[ index : index + chSize ] = maxval if newalpha[i] else minval
        return pxdata
    @staticmethod
    def makePxDataWithColor( colorbytes , repeat_times ):
        """ makePxDataWithColor :: bytearray -> UInt -> bytearray """
        return colorbytes * repeat_times

    # TODO: There's a problem with application. I don't know if it's at this level or it's in
    #       the Grow-object level
    #   ->  There's a inconsistency between steps number and border width.
    @staticmethod
    def applyMethodRecipe( grow , recipe ):
        """ Apply the grow recipe to the grow object. 
            grow :: Grow ; recipe :: [(Grow -> Grow Action,Int)] """
        for task , steps in recipe:
            for i in range(steps):
                task( grow )
        return grow

    @staticmethod
    def getTrueBounds( node ):
        """ Accumulate the union of bounds of each element of the node hierarchy defined by 'node'. """
        greatest = node.bounds()
        search   = deque( node.childNodes() )
        while search:
            n = search.pop()
            greatest = greatest.united( n.bounds() )

            for c in n.childNodes():
                search.append(c)
        return greatest

    def run( self , **data_from_gui ):
        """ Make borders to the given krita's node, using the keys defined in the global variable KEYS.
                data_from_gui -> dict(...)
                and data_from_gui.keys() == KEYS
        """

        if set(data_from_gui.keys()) != KEYS:
            print( f"[Borderizer] Couldn't match the keys of:\n{data_from_gui}, with the required keys: {KEYS}" , file = stderr )
            return False

        # [@] Initialization
        node = data_from_gui["node"]
        doc  = data_from_gui["doc"]
        kis  = data_from_gui["kis"]
        view = kis.activeWindow().activeView()

        # Method parse:
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
            mcolor = ManagedColor( node.colorModel() , node.colorDepth() , node.colorProfile() )
            mcolor.setComponents( components )
        # This explicit conversion is totally required because the krita. View objects sometimes don't 
        # update the color space of user's color (foreground and background colors)
        mcolor.setColorSpace( node.colorModel() , node.colorDepth() , node.colorProfile() )
        color  = Borderizer.__get_true_color__( mcolor )

        # Bounds selection:
        nbounds      = Borderizer.getTrueBounds( node )
        if nbounds.isEmpty() and not node.animated() :
            print( f"[Borderizer] The layer is empty." , file = stderr )
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
        frameH = FrameHandler( doc , kis , debug = False )
        # Builds the color data

        colordata = Borderizer.makePxDataWithColor( color , length )

        # Time Selection:
        protoTimeline = data_from_gui["animation"]
        if protoTimeline:
            start , finish = protoTimeline
            timeline       = frameH.get_animation_range( source , start , finish )
        else:
            timeline       = None
        
        if timeline:
            grow          = Grow.singleton()
            anim_length   = len( str( len( timeline ) ) )
            original_time = doc.currentTime()
            frameH.build_directory()
            print( f"TIMELINE: {timeline}" )

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

                doc.refreshProjection()
                doc.waitForDone()

                frameH.exportFrame( f"frame{t:0{anim_length}}.png" , target )

            # Exit:
            frameH.importFrames( start , frameH.get_exported_files() )
            border = doc.topLevelNodes()[Borderizer.ANIMATION_IMPORT_DEFAULT_INDEX]
            border.remove()
            source.parentNode().addChildNode( border , source )
            border.setName( name )
            border.enableAnimation()


            # Explicit Cleaning:
            target.remove()
            del target

            if self.cleanUpAtFinish:
                frameH.removeExportedFiles( removeSubFolder = True )

            doc.setCurrentTime( original_time )
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
