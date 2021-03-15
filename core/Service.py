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
from collections        import deque, namedtuple

class REQUEST(
    namedtuple(
        typename    = 'REQUEST',
        field_names = ['who','function','args']
              )
           ): pass

class Service( QObject ):
    """ Must be connected to a Client """
    BUFFERSIZE = 1

    serviceRequest = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )
        # Server side: Request 
        self.queries = SimpleQueue() # of REQUEST
        # Qt side:
        self.serviceRequest.connect( self.answerRequest ) # (service) <<= (client)

    def request( self , who , function , *args  ):
        self.queries.put( REQUEST(who,function,args) )
        self.serviceRequest.emit()

    @pyqtSlot()
    def answerRequest( self ):
        """ Offer a service to a client and give it the result. """
        # Produce/Apply ----------------------------
        who , function , args = self.queries.get()
        product = function( *args )
        # ------------------------------------------

        # Add to Client's "Mailbox" ----------------
        who.putResponse( product )
        # ------------------------------------------

class Client( QObject ):
    """ Must be connected to a Service """
    def __init__( self , serv = Service() , parent = None ):
        super().__init__( parent )
        self.service  = serv
        self.response = SimpleQueue()

    def putResponse( self , product ):
        self.response.put( product )

    def serviceRequest( self , func , *arg_list ):
        """ ARGUMENTS
                service(function(*args)): function applied in Service.
                *arg_list:                arguments passed to the service
                                          function.
            Send a new service function to the Service object and waits until
            it finishes. Retrieve and return the new result from it. """
        self.service.request( self , func , *arg_list )
        # Wait For Done -------------------------------------------
        return self.response.get( block = True )

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
