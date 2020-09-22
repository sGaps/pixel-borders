from PyQt5.QtCore    import QAbstractTableModel , QModelIndex , Qt , QVariant
from PyQt5.QtWidgets import ( QTableView , QAbstractItemView , QStyledItemDelegate , QHeaderView ,
                              QSpinBox , QComboBox )
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

INDEX_METHODS = ["force","any-neighbor","corners","not-corners"]

# TODO: Fix ComboBox Render bugs.
class MethodDelegate( QStyledItemDelegate ):
    MAX = 200
    MIN = 1
    NAME_COL = 0
    STEP_COL = 1 
    def __init__( self , parent = None ):
        super().__init__( parent )
    def createEditor( self , parent , option , index ):
        """ Provides a simple QSpinbox editor with a range of [1..200] """
        col = index.column()
        if col == MethodDelegate.NAME_COL:
            editor = QComboBox( parent )
            editor.setFrame( False )
            editor.addItems( INDEX_METHODS )
        elif col == MethodDelegate.STEP_COL:
            editor = QSpinBox( parent )
            editor.setFrame( False )
            editor.setMinimum( MethodDelegate.MIN )
            editor.setMaximum( MethodDelegate.MAX )
        return editor

    # NOTE: For now, this method only let you edit things with a spinbox.
    #       If you wanna do more complex operations, then decide what you want to do
    #       using the index argument.
    def setEditorData( self , editor , index ):
        """ Reads the data from the model and converts it to an integer value, so
            it can be used by the editor. """
        col = index.column()
        if col == MethodDelegate.NAME_COL:
            value   = INDEX_METHODS.index( index.model().data( index , Qt.EditRole ) )
            combo   = editor
            combo.setCurrentIndex( value )
            combo.showPopup()
        elif col == MethodDelegate.STEP_COL:
            value   = int( index.model().data( index , Qt.EditRole ) )
            spinbox = editor
            spinbox.setValue( value )

    def setModelData( self , editor , model , index ):
        """ Reads the contents of the returned editor from .createEditor(...), and writes it
            to the model. """
        col = index.column()
        if col == MethodDelegate.NAME_COL:
            combo   = editor

            # Write & Exit:
            method  = combo.currentIndex()
            model.setData( index , method , Qt.EditRole )
        elif col == MethodDelegate.STEP_COL:
            spinbox = editor
            # Force the evaluation of its contents:
            spinbox.interpretText()

            # Write & Exit:
            steps   = spinbox.value()
            model.setData( index , steps , Qt.EditRole )

    def updateEditorGeometry( self , editor , option , index ):
        """ Minimal geometry. """
        editor.setGeometry( option.rect )

class MethodModel( QAbstractTableModel ):
    """
        This model contains:
            data        :: [ ( Method_Index , Steps ) ]
            rows , cols :: Int
            HLabels     :: [ String ]

        This model has editable items.

        SIGNALS
            void rowMethodChanged( int )
            void rowStepsChanged( int )
    """
    rowMethodChanged = pyqtSignal( int )
    rowStepsChanged  = pyqtSignal( int )

    MINIMAL  = ["any-neighbor",1]
    NAME_COL = 0
    STEP_COL = 1
    def __init__( self , parent = None ):
        # Empty data
        super().__init__( parent )

        self.HLabels = [ "Method" , "Steps" ]
        self.cols    = 2
        self._data   = [ MethodModel.MINIMAL.copy() ]

    def headerData( self , section , orientation , role ):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HLabels[ section ]
        else:
            return QVariant()

    def rowCount( self , index = QModelIndex() ):
        return len( self._data )

    def columnCount( self , index = QModelIndex() ):
        return self.cols

    def flags( self , index = QModelIndex() ):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def data( self , index , role = Qt.DisplayRole ):
        if index.isValid():
            row = index.row()
            col = index.column()
            if not index.isValid():
                return QVariant()

            if role == Qt.DisplayRole:
                return self._data[row][col]

            elif role == Qt.TextAlignmentRole:
                return Qt.AlignVCenter | Qt.AlignLeft

            elif role == Qt.CheckStateRole:
                return QVariant()

            elif role == Qt.EditRole:
                return self._data[row][col]
            else:
                return QVariant()
        else:
            return QVariant()

    def setData( self , index , value , role = Qt.EditRole ):
        """ emits a rowMethodChanged or rowStepsChanged """
        row = index.row()
        col = index.column()
        if index.isValid() and role == Qt.EditRole:
            if col == MethodModel.NAME_COL:
                self._data[row][col] = INDEX_METHODS[value]
                self.rowMethodChanged.emit( row )
            elif col == MethodModel.STEP_COL:
                self._data[row][col] = value
                self.rowStepsChanged.emit( row )
            self.dataChanged.emit( index , index , [role] )
            return True
        pass

    def getData( self ):
        return self._data

    # This must to call these methods: beginInsertRows() before inserting new rows into the data
    # structure, and endInsertRows() immediatelyafterwards.
    
    # The parent index corresponds to the parent into which the new rows are inserted. first and
    # and last are the row numbers that the new rows will have after been inserted
    def insertRows( self , row , count , parent = QModelIndex() ):
        # Parent , first , last
        self.beginInsertRows( parent , row , row + count - 1 )
    
        new_rows   = [ MethodModel.MINIMAL.copy() for _ in range(count) ]
        data       = self._data
        data       = data[:row] + new_rows + data[row:]
        self._data = data
        self.endInsertRows()

        return True

    # This must to call these methods: beginRemoveRows() -> endRemoveRows()
    def removeRows( self , row , count , parent = QModelIndex() ):
        if self.rowCount() > 1:
            # parent , first , last
            self.beginRemoveRows( parent , row , row + count - 1 )
        
            data       = self._data
            #data       = data[row:] + data[row+count:]
            data       = data[:row] + data[row+count:]
            self._data = data
            self.endRemoveRows()

            return True
        else:
            return False

    # TODO: Delete
    def addRowToRecipe( self , index = QModelIndex() ):
        self._data.append( [ INDEX_METHODS[0] , 1 ] )
        self.rows += 1
        return True

    # TODO: Delete
    def removeRowToRecipe( self , index = QModelIndex() ):
        # Must be selected item.
        self.rows += 1
        return False

class MethodWidget( QTableView ):
    """
        SIGNALS
            void firstMethodChanged( str )
        SLOTS
            void addMethod()
            void removeMethod()
    """
    firstMethodChanged = pyqtSignal( str )

    def __init__( self , parent = None ):
        super().__init__( parent )
        model = MethodModel()
        self.setModel( model )
        self.setItemDelegate( MethodDelegate() )
        #self.openPersistentEditor( self.model().index( 0 , 0 ) )
        self.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )

        model.rowMethodChanged.connect( self.__first_method_update_request__ )

        # Enables the edition after a single click
        #self.setEditTriggers( QAbstractItemView.AllEditTriggers )

    def mousePressEvent( self , event ):
        index = self.indexAt( event.pos() )
        if index.isValid():
            self.edit( index )


    @pyqtSlot( int )
    def __first_method_update_request__( self , row ):
        if row == 0:
            model = self.model()
            self.firstMethodChanged.emit( model.data( model.index(0,0) , Qt.EditRole ) )

    @pyqtSlot()
    def addMethod( self ):
        model = self.model()
        last  = model.rowCount()
        model.insertRows( last , 1 )
        #if model.insertRows( last , 1 ):
        #    self.openPersistentEditor( model.index( last , 0 ) )

    @pyqtSlot()
    def removeMethod( self ):
        model = self.model()
        last  = model.rowCount() - 1
        model.removeRows( last , 1 )

    def dataLength( self ):
        return self.model().rowCount()

    def getData( self ):
        return self.model().getData().copy()

