# Module:      core.Borderizer.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------
"""
    Defines a Borderizer object to add pixel borders to a krita node.

    [:] Defined in this module
    --------------------------
    Borderizer      :: class
        Object used to add borders to a source krita layer/node. This layer can be a
        paint layer or group layer.

        Also this layer can be animated, so an animated border will be created.
        NOTE: The method requires read/write permissions to perform an animation operation.

    INDEX_METHODS   :: [str]
        List of available grow methods.

    METHODS         :: dict
        Maps each available method name => Grow.grow_method( ... )

    KEYS            :: set
        Holds each required keys to run a Borderizer object.
            "methoddsc" -> Method descriptor It's a method recipe. maps [ [str,int] ] type.
                            example: [ ["any-neighbor",1] , ["corners",2] , ["strict-horizontal",4] ]
            "colordsc"  -> Color descriptor. Says what color must be used.
                            ["FG" , _]:             Foreground
                            ["BG" , _]:             Background
                            ["CS" , components]:    Custom
                                    where components :: [int]
            "trdesc"    -> Transparency descriptor. This means wich values will be considered as transparent
                            [ transparency_value , threshold ]
            "node"      -> Krita source node.
            "kis"       -> Krita instance.
            "doc"       -> Krita document.
            "animation" -> Animation range. It holds a list with which means a inclusive range. [start,finish]
                           When this is equal to None, then there's no animation.
                            example: [ 1 , 10 ] => start at frame 1, and animate until frame 10
            "name"      -> The name that will be used for the new border layer.
    DEPTHS          :: dict
        Holds relevant information about the color Depth, like cast type and max limits.

    [*] Created By
     |- Gaps : sGaps : ArtGaps
"""




from krita              import Selection , Krita , ManagedColor
from struct             import pack , unpack
from PyQt5.QtCore       import QRect
from sys                import stderr
from collections        import deque

from .AlphaGrow         import Grow
from .AlphaScrapperSafe import Scrapper
from .FrameHandler      import FrameHandler

INDEX_METHODS = ["force","any-neighbor","corners","not-corners","strict-horizontal","strict-vertical"]

METHODS = { "force"             : Grow.force_grow             ,
            "any-neighbor"      : Grow.any_neighbor_grow      ,
            "corners"           : Grow.corners_grow           ,
            "not-corners"       : Grow.not_corners_grow       ,
            "strict-horizontal" : Grow.strict_horizontal_grow ,
            "strict-vertical"   : Grow.strict_vertical_grow   }

COLOR_TYPES = { "FG" , "BG" , "CS" }
# Keys used in the data structure passed by the GUI
KEYS = {  "q-recipedsc" , # Quick Recipe Descriptor.
          "c-recipedsc" , # Custom Recipe Descriptor.
          "is-quick"    , # If true, Use q-recipedsc instead of c-recipedsc.
          "colordsc"    , # Color Descriptor.
          "trdesc"      , # Transparency Descriptor.
          "node"        , # Current Node.
          "doc"         , # Current Document.
          "kis"         , # Current Krita instance.
          "animation"   , # Animation bounds.
          "try-animate" , # Make animated border when it's possible.
          "name"        , # Border name.
          }
#KEYS = {  "methoddsc" , # [[method,thickness]] where method is
#          "colordsc"  , # [ color_type , components ]
#                        # where color_type = "FG" | "BG" , "CS"
#                        #       components = [UInt]
#          "trdesc"    , # Transparency descriptor = [ transparency_value , threshold ]
#          "node"      , # Krita Node
#          "doc"       , # Krita Document
#          "kis"       , # Krita Instance
#          "animation" , # None if it hasn't animation. Else ( start , finish ) -> start , finish are Ints in [UInt]
#          "name"      , # String
#          }

# Support for krita color depths. Key -> ( Read_Write_Pattern , Max_Value )
DEPTHS = { "U8"  : ("B" , 2**8  - 1 ) ,
           "U16" : ("H" , 2**16 - 1 ) ,
           "F16" : ("e" , 1.0       ) ,
           "F32" : ("f" , 1.0       ) }

# New Keys
# [PxGUI] Data Sent: {
#     name: Border
#     is-quick: True
#     colordsc: ('FG', None)
#     methoddsc: [['any-neighbor', 1]]
#     trdesc: [False, 0]
#     animation: []
#     try-animate: True
#     kis: <PyKrita.krita.Krita object at 0x7fc5336fb040>
#     doc: None
#     node: None
# }

class Borderizer( object ):
    """
        Object used to make borders to regular, group or animated nodes.
        This will search into the sub node hiearchy to make the borders correctly.
    """
    ANIMATION_IMPORT_DEFAULT_INDEX = -1
    def __init__( self , info = None , cleanUpAtFinish = False ):
        """
            ARGUMENTS
                info(krita.InfoObject): Specify some special arguments to export files.
                cleanUpAtFinish(bool):  Indicates if is totally required to remove all exported files.
        """
        self.info            = info
        self.cleanUpAtFinish = cleanUpAtFinish

        # GUI Connections -------------------------------
        self.gui   = None   # Menu or any GUI compatible.
        self.waitp = None   # Wait Page of that Menu

    @staticmethod
    def __get_true_color__( managedcolor ):
        """
            ARGUMENTS
                managedcolor(krita.ManagedColor): source normalized color from krita.
            RETURNS
                ( bytearray , bytearray , bytearray , bytearray )
            Takes a krita.ManagedColor and returns four relevant bytearrays:
                ( color transparent,
                  color opaque     ,
                  min alpha value  ,
                  max alpha value  )
        """

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

        maxvalue = pack(dtype , dmax)
        minvalue = pack(dtype , 0)
        return ( color + minvalue , color + maxvalue , minvalue , maxvalue )

    @staticmethod
    def fillWith( target , pxdata , bounds ):
        """
            ARGUMENTS
                target(krita.Node):         target node.
                pxdata(bytearray):          pixel data.
                bounds(PyQt5.QtCore.QRect): bounds of the pixel data.
            Updates the node pixelData using a bytearray and a QRect """
        target.setPixelData( pxdata , bounds.x() , bounds.y() , bounds.width() , bounds.height() )

    @staticmethod
    def makePxDataWithColor( colorbytes , repeat_times ):
        """
            ARGUMENTS
                colorbytes(bytearray):  color to repeat
                repeat_times(int):      how many times that color repeats
            RETURNS
                bytearray
        """
        return colorbytes * repeat_times

    @staticmethod
    def makePxDataUsingAlpha( maxval , nocolor , opaque , alpha , length , nchans ):
        """
            ARGUMENTS
                maxval(bytearray):  max alpha value.
                nocolor(bytearray): Transparent color.
                opaque(bytearray):  Opaque color.
                alpha(bytearray):   simplified version of pixel data. (returned by a Scrapper or Grow object)
                length(int):        length of the alpha data.
                nchans(int):        How many channels has the color space.
            RETURNS
                bytearray
        """
        item_size    = len( maxval )                # Channel Size
        new_contents = nocolor * length             # Pixel data
        offset       = item_size * (nchans - 1)     # Local start position of the alpha channel
        step         = item_size * nchans
        pos          = 0
        while True:
            pos   = alpha.find( maxval , pos )
            if pos < 0:
                break

            start = pos * step + offset

            if alpha[pos]:
                new_contents[ start : start + item_size ] = opaque
            # Update!
            pos  += 1
        return new_contents

    @staticmethod
    def applyMethodRecipe( grow , recipe ):
        """
            ARGUMENTS
                grow(AlphaGrow.Grow):               object that describes how the alpha will grow.
                recipe([AlphaGrow.Grow.method()):   list of methods from a AlphaGrow.Grow object
            RETURNS
                AlphaGrow.Grow
            Apply the grow recipe to the grow object. """
        for task , steps in recipe:
            for i in range(steps):
                task( grow )
        return grow

    @staticmethod
    def getTrueBounds( node ):
        """
            ARGUMENTS
                node(krita.Node):   source node
            RETURNS
                PyQt5.QtCore.QRect
            Accumulate the union of bounds of each element of the node hierarchy defined by 'node'. """
        greatest = node.bounds()
        search   = deque( node.childNodes() )
        while search:
            n = search.pop()
            greatest = greatest.united( n.bounds() )

            for c in n.childNodes():
                search.append(c)
        return greatest

    @staticmethod
    def getBounds( node , document_bounds , thickness ):
        """
            ARGUMENTS
                node(krita.Node):                       source node.
                document_bounds(PyQt5.QtCore.QRect):    Bounds of the document.
                thickness(int):                         how many pixels will be added to each side of the document_bounds
            Returns a QRect that represents the bounds of the target layer. """
        nBounds = node.bounds() # NOTE: node.bounds() returns a QRect() that include the bounds of
                                #       child nodes.
        pBounds = QRect( nBounds.x()      - thickness   ,
                         nBounds.y()      - thickness   ,
                         nBounds.width()  + 2*thickness ,
                         nBounds.height() + 2*thickness )
        return document_bounds.intersected( pBounds )

    def run( self , **data_from_gui ):
        """
            ARGUMENTS
                data_from_gui(dict):    must have the keys of KEYS
            RETURNS
                bool
            Make borders to the given krita's node, using the keys defined in the global variable KEYS.

            See also: KEYS
        """
        data = data_from_gui

        # If it doesn't have all the information:
        if KEYS.difference( set(data.keys()) ):
            print( f"[Borderizer] Couldn't match the keys of:\n{data_from_gui}, with the required keys: {KEYS}" , file = stderr )
            return False

        #node = data_from_gui["node"]
        #doc  = data_from_gui["doc"]
        #kis  = data_from_gui["kis"]
        # [@] Initialization:
        node = data.get( "node" , None )
        doc  = data.get( "doc"  , None )
        kis  = data.get( "kis"  , None )
        if not ( node and doc and kis ):
            print( f"[Borderizer] Couldn't run with incomplete information: node = {node} , krita = {kis} , document = {doc}" , file = stderr )
            return False

        view = kis.activeWindow().activeView()

        # Method parse:
        methodRecipe = []
        thickness    = 0

        if data["is-quick"]:
            protoRecipe = data["q-recipedsc"]
        else:
            protoRecipe = data["c-recipedsc"]

        for method_name , method_thck in protoRecipe:
            method = METHODS.get( method_name , None )
            if not method:
                print( f"[Borderizer] Unknow method {method_name}" , file = stderr )
                return
            methodRecipe.append( (method,method_thck) )
            thickness += method_thck

        # Color selection:
        colorType , components = data["colordsc"]
        if   colorType == "FG":
            mcolor = view.foregroundColor()
        elif colorType == "BG":
            mcolor = view.backgroundColor()
        else:
            mcolor = ManagedColor( node.colorModel() , node.colorDepth() , node.colorProfile() )
            mcolor.setComponents( components )
        # This explicit conversion is totally required because Krita's View objects sometimes don't
        # update the color space of user's color (foreground and background colors)
        mcolor.setColorSpace( node.colorModel() , node.colorDepth() , node.colorProfile() )
        nocolor , color , trBytes , opBytes = Borderizer.__get_true_color__( mcolor )

        dbounds     = doc.bounds()

        # Misc & Time:
        name          = data["name"]
        #transparency , threshold = data["trdesc"]
        useOpaqueAsTransparency , threshold_percent = data["trdesc"]
        dmax         = DEPTHS[ node.colorDepth() ][1] # Takes the maximun value for the current depth.
        transparency = dmax if useOpaqueAsTransparency else 0
        # BUG: Threshold has a big error interval.
        threshold    = int( dmax * (threshold_percent/100) ) if node.colorDepth() in {"U8","U16"} else dmax * (threshold_percent/100)

        # They're used for the writing proccess

        batchK , batchD = kis.batchmode() , doc.batchmode()
        kis.setBatchmode( True )
        doc.setBatchmode( True )

        # [!] Run method:
        chans  = node.channels()
        nchans = len(chans)

        # [N] Node actions:
        source = node

        # TODO: Add the Border-node using an action to add it to the Undo-Stack
        target = doc.createNode( ".target" , "paintlayer" )
        # Link the target with the document: (Just above the node)
        source.parentNode().addChildNode( target , source )

        # First Abstractions
        scrap  = Scrapper()
        frameH = FrameHandler( doc , kis , debug = False )
        # Builds the color data


        # [*] PROGRESS BAR:
        progress = self.waitp.progress
        progress.setMinimum( 0 )
        progress.reset()

        # [T] Time Selection:
        if data["try-animate"]:
            # BUG: repeated frames when start = finish
            protoTimeline  = data["animation"]
            start , finish = protoTimeline
            timeline       = frameH.get_animation_range( source , start , finish )
        else:
            timeline       = None

        if timeline:
            # [*] PROGRESS BAR:
            progress.setMaximum( len(timeline) )
        else:
            # [*] PROGRESS BAR:
            progress.setMaximum( 1 )

        # BUG: Distorted images with depth = "U16"
        if timeline:
            # [|>] Animation.
            canvasSize    = dbounds.width() * dbounds.height()
            grow          = Grow.singleton( amount_of_items_on_search = canvasSize )
            anim_length   = len( str( len( timeline ) ) )
            original_time = doc.currentTime()
            # Makes a new directory for the animation frames when it's possible.
            if not frameH.build_directory():
                target.remove()
                del target
                # TODO: Notify when something goes wrong!
                return False

            colordata = None
            for t in timeline:
                # Update the current time and wait in synchronous mode:
                doc.setCurrentTime(t)
                doc.refreshProjection()
                doc.waitForDone()

                # [C] Clean Previous influence
                if colordata:
                    Borderizer.fillWith( target , Borderizer.makePxDataWithColor( nocolor , length ) , bounds )

                # [X] Bounds Update:
                bounds = Borderizer.getBounds( source , dbounds , thickness )

                # [B] Bounds dependent:
                width  = bounds.width()
                length = bounds.width() * bounds.height()
                pxSize = length * nchans

                # [R] Projection Refreshment dependent:
                alpha  = scrap.extractAlpha( source , bounds , transparency , threshold )
                grow.setData( alpha , width , length )

                # Make the borders and update the target data.
                Borderizer.applyMethodRecipe( grow , methodRecipe )
                newAlpha = grow.difference_with( alpha )

                colordata = Borderizer.makePxDataUsingAlpha( b"\xff" , nocolor , opBytes , newAlpha , length , nchans )

                Borderizer.fillWith( target , colordata , bounds )

                doc.refreshProjection()
                doc.waitForDone()

                frameH.exportFrame( f"frame{t:0{anim_length}}.png" , target )

                # [*] PROGRESS BAR:
                progress.setValue( progress.value() + 1 )

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

            # DONE:
            progress.setValue( progress.value() + 1 )
            doc.setCurrentTime( original_time )
            done = True
        else:
            # [||] Static Layer.

            # [X] Bounds Update:
            bounds = Borderizer.getBounds( source , dbounds , thickness )

            # [B] Bounds dependent:
            width  = bounds.width()
            length = bounds.width() * bounds.height()
            pxSize = length * nchans

            alpha    = scrap.extractAlpha( source , bounds , transparency , threshold )
            grow     = Grow( alpha , width , length )
            Borderizer.applyMethodRecipe( grow , methodRecipe )
            newAlpha = grow.difference_with( alpha )

            # Update and Write
            colordata = Borderizer.makePxDataUsingAlpha( b"\xff" , nocolor , opBytes , newAlpha , length , nchans )
            Borderizer.fillWith( target , colordata , bounds )

            # Exit:
            border = target
            border.setName( name )


            # DONE:
            progress.setValue( progress.maximum() )
            done = True

        doc.refreshProjection()
        kis.setBatchmode( batchK )
        doc.setBatchmode( batchD )
        return done
