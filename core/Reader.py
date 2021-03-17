from .Arguments   import KisData
from .KisStatus   import KisStatus , ALPHA
from .Service     import Client
from queue        import SimpleQueue
from PyQt5.QtCore import QRect

class Reader( object ):
    """ Reads frames from krita. and put them into outQueue. If outQueue is not provided, it will allocate
        a SimpleQueue inside. """
    def __init__( self , kis_arguments  = KisData()     ,
                         outQueue       = SimpleQueue() ,
                         status         = KisStatus()   ,
                         report         = (lambda msg: None) ,
                         error          = (lambda msg: None) ,
                         stepDone       = (lambda:     None) ): # 'Atomic' Increment
        """
            ARGUMENTS
                kis_arguments(KisData): Holds relevant information about krita. 
                                            .doc(krita.Document)
                                            .node(krita.Node)
                                            .kis(krita.Krita)
                                            .service(core.Service.Service)
                                            .timeline(range)
                                            .client(core.Service.Client)
                                        Must have service and client objects to keep fast communication with krita.
                outQueue(queue.SimpleQueue): Where this will put its results. each element is a ALPHA(bytearray,time,bounds)
                status(KisStatus):           Shared object that says when this method must stop.
                report(function(str) -> IO()): Takes an string and performs an I/O Action. It will be a signal emission or something,
                                               a function to print, debug, etc.
                error(function(str) -> IO()):  Like report, but it's used for error messages.
                progress(function(int) -> IO()):  Like report, but it's used to send a progress step.
        """
        self.args   = kis_arguments
        self.queue  = outQueue
        self.status = status

        # Messages and more:
        self.report   = report
        self.error    = error
        self.stepDone = stepDone

    @staticmethod
    def getBounds( node , document_bounds , thickness ):
        """
            ARGUMENTS
                node(krita.Node):                       source node.
                document_bounds(PyQt5.QtCore.QRect):    Bounds of the document.
                thickness(int):                         how many pixels will be added to every
                                                        side of the document_bounds
            RETURNS
                QRect, which represents the bounds of the target layer. """
        nBounds = node.bounds()

        pBounds = QRect( nBounds.x()      - thickness   ,
                         nBounds.y()      - thickness   ,
                         nBounds.width()  + 2*thickness ,
                         nBounds.height() + 2*thickness )
        return document_bounds.intersected( pBounds )

    def run( self ):
        """
            Extract all alpha information of a Source Node in a Krita's Document timeline.
        """

        # Targets --------------------
        doc        = self.args.doc
        source     = self.args.node
        timeline   = self.args.timeline

        # Shared Data ----------------
        transparency = self.args.transparency   # Number
        threshold    = self.args.threshold      # Number
        thickness    = self.args.thickness      # Int
        scrap        = self.args.scrapper       # AlphaScrapper.Scrapper
        dbounds      = doc.bounds()             # QRect
        constraint   = self.args.constraint     # Take bounds from this node.

        server     = self.args.service
        client     = Client( server )

        status     = self.status
        raw_frames = self.queue

        # I/O Reports ------------
        report     = self.report
        error      = self.error
        stepDone   = self.stepDone

        if not doc:
            error( "[core.Reader]: NO DOCUMENT PROVIDED." )
            status.internalStopRequest( "[core.Reader]: A Krita's document is required to get actual bounds of the canvas." )
            return

        colordata = bytearray()
        bounds    = QRect(0,0,0,0)
        getBounds = Reader.getBounds

        # Single frame!
        if not timeline:
            timeline = range( doc.currentTime() , doc.currentTime()+1 )

        for t in timeline:
            if not status.keepRunning():
                report( "core.Reader: Canceled by user." )
                return

            client.serviceRequest( doc.setCurrentTime , t )
            client.serviceRequest( doc.refreshProjection  )
            client.serviceRequest( doc.waitForDone        )

            # Clean previous data
            #bounds = getBounds( source , dbounds , thickness )
            bounds = getBounds( constraint , dbounds , thickness )
            alpha  = scrap.extractAlpha( source , bounds , transparency , threshold )

            # Submit changes ------------------------
            raw_frames.put( ALPHA(alpha, t, bounds) )
            
            # [*] PROGRESS BAR:
            stepDone()

