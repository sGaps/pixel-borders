from .AnimationHandler import AnimationHandler
from .Arguments import KisData
from .KisStatus import KisStatus
from queue      import SimpleQueue
from .Service   import Client
from threading  import Barrier
from PyQt5.QtCore import QRect

class Writer( object ):
    # TODO: Add an option for only write on memory instead of write in main and secondary memory.
    def __init__( self , kis_arguments  = KisData()          ,
                         id_writer      = 0                  ,
                         workstatus     = [True]             ,
                         target         = None               ,
                         writeDone      = Barrier(parties=1) ,
                         refreshDone    = Barrier(parties=1) ,
                         flushDone      = Barrier(parties=1) ,
                         inQueue        = SimpleQueue()      ,
                         status         = KisStatus()        ,
                         report         = (lambda msg: None) ,
                         error          = (lambda msg: None) ,
                         stepDone       = (lambda:     None) ): # 'Atomic' Increment
        """
            ARGUMENTS:
                target (krita.Node):
                waitForFlush(threading.Condition): condition variable used to wait until flush has been done.
                framesByFlush(int):                how many frames will be sent to Flush.
            Writes new alpha data into a target node and waits until
            the new information is flushed by a Flush object.
        """
        super().__init__()
        self.args          = kis_arguments
        self.id_writer     = id_writer
        self.workstatus    = workstatus
        self.target        = target
        self.writeDone     = writeDone
        self.refreshDone   = refreshDone
        self.flushDone     = flushDone
        self.status        = status

        self.raw           = inQueue

        # Messages and more:
        self.report       = report
        self.error        = error
        self.stepDone     = stepDone

    @staticmethod
    def makePxData( nocolor , opBytes , minimalAlpha , length , nchans , chsize ):
        """
            ARGUMENTS
                nocolor(bytearray):         raw-data of an empty pixel
                                            (where: len nocolor = len opBytes * nchans).
                opBytes(bytearray):         opaque value as bytearray.
                minimalAlpha(bytearray):    Data extracted from a Grow object.
                length(int):                number of entries in minimalAlpha.
                nchans(int):                number of channels of the current color.
                chsize(int):                size in bytes per channel.
            RETURNS
                bytearray. New pixel data for a target node.
        """
        # matchValue is the 'opaque' value of an minimalAlpha object.
        matchValue = 0xFF
        contents = nocolor * length             # ex.:  [ Pixel1(ch1 , ch2 , ch3 , ch4) , Pixel2(...) , ... ]
        offset   = chsize * (nchans - 1)        #                                ^    ^
        step     = chsize * nchans              # --> --------------------------------|
        pos      = -1
        start    = 0
        while True:
            pos = minimalAlpha.find( matchValue , pos + 1 )
            if pos < 0:
                break

            # Update.
            start = pos * step + offset
            if minimalAlpha[pos]:
                contents[ start : start + chsize ] = opBytes
        return contents

    @staticmethod
    def fillWith( target , pxdata , bounds ):
        """
            ARGUMENTS
                target(krita.Node):         target node.
                pxdata(bytearray):          pixel data.
                bounds(PyQt5.QtCore.QRect): bounds of the pixel data.
            Updates the node pixelData using a bytearray and a QRect """
        target.setPixelData( pxdata , bounds.x() , bounds.y() , bounds.width() , bounds.height() )

    def run( self ):
        """
            Writes data into target nodes.
        """
        target = self.target 
        raw    = self.raw
        status = self.status
        client = Client( self.args.service )

        # Format:
        dummy_timeline = self.args.timeline or [None]
        anim_length    = len( str( len(dummy_timeline) ) )

        if not target:
            error( "[core.Writer]: Null target" )
            status.internalStopRequest( "[core.Writer]: Can't work without any layer." )
            return

        # I/O Reports ------------
        report     = self.report
        error      = self.error
        stepDone   = self.stepDone

        # Shared Data ----------------
        doc        = self.args.doc
        trPixel    = self.args.trPixel # No Color.
        opPixel    = self.args.opPixel # Color.
        trBytes    = self.args.trBytes # Transparent in Alpha Channel.
        opBytes    = self.args.opBytes # Opaque in Alpha Channel.

        nchans     = self.args.nchans
        chsize     = self.args.chsize
        animator   = self.args.animHandler
        # ----------------------------

        # Cache:
        makePxData = Writer.makePxData
        fillWith   = Writer.fillWith

        # Barriers -------------------
        writeDone   = self.writeDone
        refreshDone = self.refreshDone
        flushDone   = self.flushDone
        # ----------------------------
        id_writer   = self.id_writer
        workstatus  = self.workstatus

        while True:
            # Extract ------------------------------------
            try:
                alphaG , time , bounds = raw.get_nowait()
            except:
                alphaG , time , bounds = bytearray() , -1 , QRect(0,0,0,0)
                workstatus[id_writer]  = False

            # Write --------------------------------------

            # Bounds:
            width  = bounds.width()
            length = width * bounds.height()

            # Make item available:
            fillWith( target,                                                       # target node.
                      makePxData(trPixel, opBytes, alphaG, length, nchans, chsize), # color data.
                      bounds )                                                      # target's bounds.
            # --------------------------------------------
            

            # ............................................
            #           EXIT UPDATE CONDITION (1)
            if not status.keepRunning():
                report( "core.Writer: Canceled by user." )
                workstatus[id_writer] = False
            # ............................................

            # Parties = 4
            wakeup_index = writeDone.wait()

            # ............................................
            #               EXIT CONDITION (2)
            if not any(workstatus):
                # Just exit, nothing to do
                break
            # ............................................

            # The first thread refresh the document:
            if wakeup_index == 0:
                client.serviceRequest( doc.refreshProjection )
                client.serviceRequest( doc.waitForDone )

            wakeup_index = refreshDone.wait()

            # Flush time!
            if workstatus[id_writer]:
                if not client.serviceRequest( animator.export , f"frame{time:0{anim_length}}.png", target ):
                    error( f"[core.Writer]: Cannot export frames with <{target.name()}>" )
                    status.internalStopRequest( f"[core.Writer]: Error while trying to export the frame {time} of <{target.name()}>\n"          +
                                                 "             : Maybe this layer doesn't have permissions to write in the target directory.\n" +
                                                 "             : Or there's an error with the worker threads sync."                             )
                # [*] PROGRESS BAR:
                stepDone()
            # Clean the layer:
            fillWith( target , trPixel * length , bounds )

            # Wait for the next iteration
            wakeup_index = flushDone.wait()
        # All Done

