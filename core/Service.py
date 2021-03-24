# Module:   core.Service.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -----------------------------------------------
"""
    Offers Thread Syncronization strategies.
    This Connects Python and Qt in a safer way.

    [:] Defined in this module
    --------------------------
        Service :: class
            Manages requests from clients. and give them results.
        Client  :: class
            Request services to the Service objects. Fetch results from them.

        Client and Service must be in different threads to work correctly.

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
    """ Runs a sequence of functions requested by clients. """
    BUFFERSIZE = 1

    serviceRequest = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )
        # Server side: Request 
        self.queries = SimpleQueue() # of REQUEST
        # Qt's side:
        self.serviceRequest.connect( self.answerRequest ) # (service) <<= (client)

    def request( self , who , function , *args  ):
        """
            ARGUMENTS:
                who( Client )
                function( function(*args) -> any ): action to run in the Service's thread.
                args( list ):                       argument list passed to function.
            Recieve a request from a client.
        """
        self.queries.put( REQUEST(who,function,args) )
        self.serviceRequest.emit()

    @pyqtSlot()
    def answerRequest( self ):
        """ Offers a service to a client and give its result. """
        # Produce/Apply ----------------------------
        who , function , args = self.queries.get()
        product = function( *args )
        # ------------------------------------------

        # Add to Client's "Mailbox" ----------------
        who.putResponse( product )
        # ------------------------------------------

class Client( QObject ):
    """ Object used to send request to a sercice. """
       
    def __init__( self , serv = Service() , parent = None ):
        super().__init__( parent )
        self.service  = serv
        self.response = SimpleQueue()

    def putResponse( self , product ):
        """ Updates the internal data. used by a Service instance """
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
