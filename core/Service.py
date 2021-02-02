# Module:      core.Service.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
"""
    Offers Thread Syncronization strategies.

    [:] Defined in this module
    --------------------------
        Service :: class
            Manages services to clients. and give them results.
        Client  :: class
            Request services to the Service objects. retrieve results from them.

        Client and Service must be in different threads to work.
    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
from PyQt5.QtCore       import QObject , pyqtSignal , pyqtSlot , QMutex , QSemaphore
from queue              import SimpleQueue

class Service( QObject ):
    """ Must be connected to a Client """
    BUFFERSIZE = 1

    serviceRequest = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )

        # Server side:
        self.buffer = SimpleQueue()

        self.service  = lambda: None
        self.arg_list = []

        # Qt side:
        self.serviceRequest.connect( self.answerRequest ) # (service) <<= (client)

    def setService( self , service = lambda: None , *arg_list ):
        """ ARGUMENTS
                service(function(*args)): function applied in Service.
                *arg_list:                arguments passed to the service
                                          function.
            Updates the default service and argument list. """
        self.service  = service
        self.arg_list = arg_list

    # Producer:
    @pyqtSlot()
    def answerRequest( self ):
        """ Offer a service to a client and give it the result. """
        # Produce/Apply ----------------------------
        product = self.service( *self.arg_list )
        # ------------------------------------------

        # Add to 'Buffer' --------------------------
        self.buffer.put( product , block = True )
        # ------------------------------------------


class Client( QObject ):
    """ Must be connected to a Service """
    def __init__( self , serv = Service() , parent = None ):
        super().__init__( parent )
        self.service       = serv

        # Client side:
        self.result        = None

    def sendRequest( self ):
        """ Send a new service request to a Service Object. """
        self.service.serviceRequest.emit() # (client) =>> (service)
        # Wait For Done -------------------------------------------
        return self.service.buffer.get( block = True )

    def serviceRequest( self , func , *arg_list ):
        """ ARGUMENTS
                service(function(*args)): function applied in Service.
                *arg_list:                arguments passed to the service
                                          function.
            Send a new service function to the Service object and waits until
            it finishes. Retrieve and return the new result from it. """
        self.service.setService( func , *arg_list ) # Current Thread (Sync)
        return self.sendRequest()                          # (Force Sync)

if __name__ == "__main__":
    from PyQt5.QtCore       import QThread
    from PyQt5.QtWidgets    import QApplication

    main = QApplication( [] )

    server  = Service()
    client  = Client( server )

    tServer = QThread()
    server.moveToThread( tServer )

    tClient = QThread()
    client.moveToThread( tClient )

    # thread start
    tServer.start()
    tClient.start()

    print( f"New QObject: {client.serviceRequest( lambda: QObject().thread() )}" )
    print( f"Server: {server.thread()}"     )
    print( f"Client: {client.thread()}"     )
    print( f"Dummy:  {QObject().thread()}"  )
    client.serviceRequest( lambda a: print(a) , 'hello' )
    client.serviceRequest( lambda a , b , c: print(a+b+c) , 1 , 2 , 3 )
