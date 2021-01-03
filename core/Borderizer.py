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
try:
    from krita              import Selection , Krita , ManagedColor
except:
    print( "[Borderizer] Krita Not available" )
from struct             import pack , unpack
from PyQt5.QtCore       import QRect , QObject , pyqtSlot , pyqtSignal
from PyQt5.QtCore       import QThread , QMutex
from sys                import stderr
from collections        import deque

from .AlphaGrow         import Grow
from .Arguments         import KisData
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

# Support for krita color depths. Key -> ( Read_Write_Pattern , Max_Value )
DEPTHS = { "U8"  : ("B" , 2**8  - 1 ) ,
           "U16" : ("H" , 2**16 - 1 ) ,
           "F16" : ("e" , 1.0       ) ,
           "F32" : ("f" , 1.0       ) }

#class Borderizer( QObject ):
# BUG: QObject::starttimer cannot start from another thread
class Borderizer( QThread ):
    """
        Object used to make borders to regular, group or animated nodes.
        This will search into the sub node hiearchy to make the borders correctly.
    """
    progress        = pyqtSignal( int )
    error           = pyqtSignal( str )
    rollbackRequest = pyqtSignal()

    ANIMATION_IMPORT_DEFAULT_INDEX = -1
    def __init__( self , arguments = KisData() , thread_name = "Border-Thread" , info = None , cleanUpAtFinish = False , parent = None ):
        """
            ARGUMENTS
                info(krita.InfoObject): Specify some special arguments to export files.
                cleanUpAtFinish(bool):  Indicates if is totally required to remove all exported files.
        """
        super().__init__( parent )
        self.arguments = arguments

        self.arguments       = arguments
        self.info            = info
        # TODO: Useless (?)
        self.cleanUpAtFinish = cleanUpAtFinish

        self.setObjectName( thread_name )
        self.critical        = QMutex()
        self.keepRunning     = True
        #self.setObjectName( "Borderizer" )
        #self.stoppable       = QMutex()
        #self.keepRunning     = True

        # Default connections:
        self.rollbackList = []
        #self.failure.connect( self.terminate )

    @pyqtSlot()
    def stopRequest( self ):
        print( "Trying to stop" )
        self.enterCriticalRegion()
        self.keepRunning = False
        self.exitCriticalRegion()

    @pyqtSlot()
    def enterCriticalRegion( self ):
        self.critical.lock()

    @pyqtSlot()
    def exitCriticalRegion( self ):
        self.critical.unlock()

    @pyqtSlot()
    def rollback( self ):
        [ step() for step in self.getRollbackSteps() ]

    def getRollbackSteps( self ):
        return self.rollbackList

    def submitRollbackStep( self , rollback_step ):
        self.getRollbackSteps().append( rollback_step )

    def keepRunningNormally( self ):
        # | CRITICAL >-----------------------
        self.enterCriticalRegion()
        print( "*** On critical region" )
        keepItUp = self.keepRunning
        if keepItUp:
            self.exitCriticalRegion()
            # < CRITICAL |-----------------------
        else:
            # < CRITICAL |-----------------------
            # Cancel request accepted
            self.exitCriticalRegion()
            self.error.emit( "Canceled by user" )
            self.rollbackRequest.emit()
            #self.finished.emit()
        return keepItUp

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

    # TODO: See what I did here, lol
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

                Colored version of the node's pixel data
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
        [   
            [ task(grow) for i in range(steps) ]
            for task , steps in recipe 
        ]
        #for task , steps in recipe:
        #    for i in range(steps):
        #        task( grow )
        return grow

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

    @pyqtSlot()
    def run( self ):
        """
            ARGUMENTS
                ** implicit **
                self.arguments(KisData):
            RETURNS
                bool
            Make borders to the given krita's node, using the keys defined in the global variable KEYS.

            See also: KEYS
        """
        a = self.arguments
        if not a:
            self.error.emit( "Not valid arguments" )
            #self.finished.emit()
            return

        # Part Zero:
        name   = a.name

        # Part One:
        kis    = a.kis
        doc    = a.doc
        source = a.node
        parent = a.parent

        # Part Two:
        methodRecipe = a.recipe
        thickness    = sum( map(lambda tup: tup[1] , a.recipe) )
        nocolor , color , trBytes , opBytes = a.trPixel , a.opPixel , a.trBytes , a.opBytes
        transparency = a.transparency
        threshold    = a.threshold

        # Part Three:
        # | ROLLBACK >-----------------------
        self.enterCriticalRegion()   # |> -->
        batchK , batchD = a.batchK , a.batchD
        chans  = a.channels
        nchans = a.nchans

        self.submitRollbackStep( lambda: doc.refreshProjection()  )
        self.submitRollbackStep( lambda: kis.setBatchmode(batchK) )
        self.submitRollbackStep( lambda: doc.setBatchmode(batchD) )
        self.exitCriticalRegion()    # <-- <|
        # < ROLLBACK |-----------------------
        
        # Part Four 
        # | ROLLBACK >-----------------------
        self.enterCriticalRegion()   # |> -->
        source = a.node
        parent = a.parent
        target = doc.createNode( ".target" , "paintlayer")
        parent.addChildNode( target , source )

        self.submitRollbackStep( lambda: target.remove() )
        self.exitCriticalRegion()    # <-- <|
        # < ROLLBACK |-----------------------

        # Part Five:
        dbounds  = doc.bounds()
        scrap    = a.scrapper
        frameH   = a.frameHandler
        timeline = a.timeline
        start    = a.start
        finish   = a.finish

        # BUG: Distorted images with depth = "U16"
        currentStep = 1
        if timeline:
            # [|>] Animation.
            canvasSize    = dbounds.width() * dbounds.height()
            grow          = Grow.singleton( amount_of_items_on_search = canvasSize )
            anim_length   = len( str( len( timeline ) ) )

            
            # | ROLLBACK >-----------------------
            self.enterCriticalRegion()   # |> -->
            original_time = doc.currentTime()

            # Makes a new directory for the animation frames when it's possible.
            if not frameH.build_directory():
                self.exitCriticalRegion()    # <-- <|
                # < ROLLBACK |-----------------------
                return
            else:
                self.submitRollbackStep( lambda: frameH.removeExportedFiles(removeSubFolder = True) )
                self.exitCriticalRegion()    # <-- <|
                # < ROLLBACK |-----------------------

            colordata = None
            for t in timeline:
                # [!!] ----------------..
                # Polling
                if not self.keepRunningNormally():
                    return

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
                self.progress.emit( currentStep )
                currentStep += 1

            # Exit:
            # | ROLLBACK >-----------------------
            self.enterCriticalRegion()   # |> -->
            frameH.importFrames( start , frameH.get_exported_files() )
            border = doc.topLevelNodes()[Borderizer.ANIMATION_IMPORT_DEFAULT_INDEX]
            border.remove() # Remove the border from its parent 'slot'
            parent.addChildNode( border , source )
            border.setName( name )
            border.enableAnimation()

            self.submitRollbackStep( lambda: border.remove() )
            self.exitCriticalRegion()    # <-- <|
            # < ROLLBACK |-----------------------

            # Explicit Cleaning:
            target.remove()
            del target

            if self.cleanUpAtFinish:
                frameH.removeExportedFiles( removeSubFolder = True )
            # DONE:
            doc.setCurrentTime( original_time )
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

            self.progress.emit( currentStep )
            # DONE:

        if not self.keepRunningNormally():
            return

        doc.refreshProjection()
        kis.setBatchmode( batchK )
        doc.setBatchmode( batchD )

        #self.finished.emit()
        return
