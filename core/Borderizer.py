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
    from krita          import Selection , Krita , ManagedColor
except:
    print( "[Borderizer] Krita Not available" )
from PyQt5.QtCore       import QRect , QObject , pyqtSlot , pyqtSignal
from PyQt5.QtCore       import QThread , QMutex
from struct             import pack , unpack
from sys                import stderr

from .AlphaGrow         import Grow
from .Arguments         import KisData
from .AlphaScrapper     import Scrapper
from .FrameHandler      import FrameHandler
import cProfile

class Borderizer( QThread ):
    """
        Object used to make borders to regular, group or animated nodes.
        This will search into the sub node hiearchy to make the borders correctly.
    """
    progress        = pyqtSignal( int )
    debug           = pyqtSignal( str )
    rollbackRequest = pyqtSignal()
    workDone        = pyqtSignal()
    rollbackDone    = pyqtSignal()

    ANIMATION_IMPORT_DEFAULT_INDEX = -1
    def __init__( self , arguments = KisData() , thread_name = "Border-Thread" , info = None , cleanUpAtFinish = False , profiler = True , parent = None ):
        """
            ARGUMENTS
                info(krita.InfoObject): Specify some special arguments to export files.
                cleanUpAtFinish(bool):  Indicates if is totally required to remove all exported files.
        """
        super().__init__( parent )
        self.setArguments( arguments )
        self.info            = info

        self.cleanUpAtFinish = cleanUpAtFinish

        self.setObjectName( thread_name )
        self.critical        = QMutex()
        self.keepRunning     = True

        # Profiler
        self.profiler = profiler

        # Actions to perform if something goes wrong:
        self.rollbackList = []

    def setArguments( self , arguments ):
        self.arguments = arguments

    @pyqtSlot()
    def stopRequest( self ):
        self.debug.emit( "Trying to stop" )
        # Force to Stop. No matters what!
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
        steps = self.getRollbackSteps()
        steps.reverse()
        [ step() for step in steps ]
        self.rollbackDone.emit()

    def getRollbackSteps( self ):
        return self.rollbackList

    def submitRollbackStep( self , rollback_step ):
        self.getRollbackSteps().append( rollback_step )

    def keepRunningNormally( self ):
        # | CRITICAL >-----------------------
        self.enterCriticalRegion()
        keepItUp = self.keepRunning
        if keepItUp:
            self.exitCriticalRegion()
            # < CRITICAL |-----------------------
        else:
            # < CRITICAL |-----------------------
            # Cancel request accepted
            self.exitCriticalRegion()
            self.debug.emit( "Canceled by user" )
            self.rollbackRequest.emit()
        return keepItUp

    @staticmethod
    def __get_true_color__( managedcolor ):
        """
            ARGUMENTS
                managedcolor(krita.ManagedColor): source normalized color from krita.
           u
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
        if self.profiler:
            cProfile.runctx( "self.runBorderizer()" , globals() , locals() )
        else:
            self.runBorderizer()

    @pyqtSlot()
    def runBorderizer( self ):
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

        if not self.keepRunningNormally():
            self.rollbackRequest.emit()
            return

        if not a:
            self.debug.emit( "Not valid arguments" )
            self.rollbackRequest.emit()
            return

        # Part Zero:
        name    = a.name
        service = a.service # 
        client  = a.client  # Used to make synchronous calls to krita from a different thread

        # Part One:
        kis    = a.kis
        doc    = a.doc
        source = a.node
        parent = a.parent

        # Part Two:
        methodRecipe = a.recipe
        thickness    = a.thickness
        nocolor , color , trBytes , opBytes = a.trPixel , a.opPixel , a.trBytes , a.opBytes
        transparency = a.transparency
        threshold    = a.threshold

        # Part Three:
        # | ROLLBACK >-----------------------
        batchK , batchD = a.batchK , a.batchD
        chans  = a.channels
        nchans = a.nchans

        self.submitRollbackStep( lambda: kis.setBatchmode(batchK) )
        self.submitRollbackStep( lambda: doc.setBatchmode(batchD) )
        self.submitRollbackStep( lambda: client.serviceRequest( doc.waitForDone       ) )
        self.submitRollbackStep( lambda: client.serviceRequest( doc.refreshProjection ) )
        # < ROLLBACK |-----------------------
        
        # Part Four 
        source = a.node
        parent = a.parent

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
            self.debug.emit( "Setup animation data..." )
            # Part Six:
            target = doc.createNode( ".target" , "paintlayer" ) # Can be deleted here
            parent.addChildNode( target , source )
            self.submitRollbackStep( lambda: target.remove() )

            # [|>] Animation. BUG: There's a random QObject that is built here and it's causing a lot of problems. (maybe it's the border-node)
            canvasSize    = dbounds.width() * dbounds.height()
            grow          = Grow.singleton( amount_of_items_on_search = canvasSize )
            anim_length   = len( str( len( timeline ) ) )

            # | ROLLBACK >-----------------------
            original_time = doc.currentTime()

            # Makes a new directory for the animation frames when it's possible.
            if not frameH.build_directory():
                self.debug.emit( "Cannot create a directory for the animation frames.\n"  +
                                 "try save the file before apply this plugin or verify\n" +
                                 "if krita has permissions over the current directory."   )
                self.rollbackRequest.emit()
                # < ROLLBACK |-----------------------
                return
            else:
                self.submitRollbackStep( lambda: doc.setCurrentTime(original_time) )
                self.submitRollbackStep( lambda: frameH.removeExportedFiles(removeSubFolder = True) )
                # < ROLLBACK |-----------------------

            self.debug.emit( "Exporting frames" )
            colordata = None
            for t in timeline:
                # Polling ------------------------
                if not self.keepRunningNormally():
                    return

                # Update the current time and wait in synchronous mode:
                # NOTE: Using this scheme, the user can cancel the process. but this add a big overhead
                doc.setCurrentTime( t )
                client.serviceRequest( doc.refreshProjection )
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

                if not frameH.exportFrame( f"frame{t:0{anim_length}}.png" , target ):
                    self.debug.emit( f"Error while trying to export the frame {t}" )
                    self.rollbackRequest.emit()
                    return

                # [*] PROGRESS BAR:
                self.progress.emit( currentStep )
                currentStep += 1

            # Exit:
            # | ROLLBACK >-----------------------
            importResult = client.serviceRequest( frameH.importFrames , start , frameH.get_exported_files() )
            self.debug.emit( "Frames imported" )   # Here passed someting weird. Program freezes and got killed.
            border = doc.topLevelNodes()[Borderizer.ANIMATION_IMPORT_DEFAULT_INDEX]
            # Remove the border from its parent 'slot'
            border.remove()
            parent.addChildNode( border , source )
            border.setName( name )
            border.enableAnimation()

            self.submitRollbackStep( lambda: border.remove() )
            # < ROLLBACK |-----------------------

            # Explicit Cleaning (this can be delete in the current thread)
            target.remove()

            if self.cleanUpAtFinish:
                frameH.removeExportedFiles( removeSubFolder = True )
            # DONE:
            doc.setCurrentTime( original_time )
        else:
            # [||] Static Layer.
            self.debug.emit( "Setup layer data..." )
            target = client.serviceRequest( doc.createNode , ".target" , "paintlayer" ) # Cannot be deleted in the current thread.
            parent.addChildNode( target , source )
            self.submitRollbackStep( lambda: target.remove() )

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

        # FINISH
        a.addResult( border )
        doc.refreshProjection()
        kis.setBatchmode( batchK )
        doc.setBatchmode( batchD )

        # Non-thread event:
        self.workDone.emit()
        self.debug.emit( "Done" )
        return
