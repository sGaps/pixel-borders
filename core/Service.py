from PyQt5.QtCore       import QObject , pyqtSignal , pyqtSlot , QMutex , QSemaphore

semWait   = QSemaphore.acquire
semSignal = QSemaphore.release

class Service( QObject ):
    """ Must be connected to a Client """
    BUFFERSIZE = 1

    serviceRequest = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )

        self.buffAccess    = QSemaphore( 1 )    # This can access.
        self.buffExtract   = QSemaphore( 0 )    # Cannot Extract yet.
        self.buffWithSpace =  QSemaphore( Service.BUFFERSIZE )

        self.service  = lambda: None
        self.arg_list = []
        # Server side:
        self.result   = None

        # Qt side:
        self.serviceRequest.connect( self.answerRequest ) # (service) <<= (client)

    def setService( self , service = lambda: None , *arg_list ):
        self.service  = service
        self.arg_list = arg_list

    # Producer:
    @pyqtSlot()
    def answerRequest( self ):
        # Produce/Apply ----------------------------
        product = self.service( *self.arg_list )
        # ------------------------------------------

        self.buffWithSpace.acquire()    # <|    (E)
        self.buffAccess.acquire()       # <|    (S) 
        # Add to 'Buffer' --------------------------
        self.result = product
        # ------------------------------------------

        self.buffAccess.release()       # |>    (S)
        self.buffExtract.release()      # |>    (N)

    def getResult( self ):
        return self.result
        

class Client( QObject ):
    """ Must be connected to a Service """
    def __init__( self , serv = Service() , parent = None ):
        super().__init__( parent )
        self.service       = serv
        self.buffAccess    = serv.buffAccess
        self.buffExtract   = serv.buffExtract
        self.buffWithSpace = serv.buffWithSpace

        # Client side:
        self.result        = None

    def sendRequest( self ):
        self.service.serviceRequest.emit() # (client) =>> (service)

        # Wait For Done ---------------------------
        self.buffExtract.acquire()      # <|    (N)
        self.buffAccess.acquire()       # <|    (S)
        # ------------------------------------------

        # Extract ----------------------------------
        product = self.service.getResult()
        # ------------------------------------------

        self.buffAccess.release()       # |>    (S)
        self.buffWithSpace.release()    # |>    (S)

        # Use --------------------------------------
        self.result = product
        # ------------------------------------------

    def getResult( self ):
        return self.result

    def serviceRequest( self , func , *arg_list ):
        self.service.setService( func , *arg_list ) # Current Thread (Sync)
        self.sendRequest()                          # (Force Sync)
        return self.getResult()                     # (Sync)

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


