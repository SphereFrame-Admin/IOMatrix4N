from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QModelIndex
import nuke

class AovListModel(QtGui.QStandardItemModel):

    def __init__(self):

        super().__init__()
        self.aovList = []
        self.root = self.invisibleRootItem()
    
    def appendRow(self, item: QtGui.QStandardItem):

        self.root.appendRow(item)
        self.aovList.append(item)
        print(self.aovList)
        
    def removeRow(self, row: int):
        
        self.root.removeRow(row)
        self.aovList.pop(row)

class Window(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowFlags(QtGui.Qt.WindowStaysOnTopHint)
        self.resize(300, 100)
        self.setWindowTitle("Read Media (IOMatrix)")
        
        self.font = QtGui.QFont()
        self.font.setPointSize(12)
        self.setFont(self.font)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.pathFieldL = QtWidgets.QLabel("File", self)
        self.layout.addWidget(self.pathFieldL)

        self.pathLayout = QtWidgets.QHBoxLayout(self)
        self.pathField = QtWidgets.QLineEdit(self)
        self.chooseBtn = QtWidgets.QPushButton("Choose...", self)
        self.chooseBtn.clicked.connect(self.chooseFile)
        self.pathLayout.addWidget(self.pathField)
        self.pathLayout.addWidget(self.chooseBtn)
        self.layout.addLayout(self.pathLayout)

        self.colSpcL = QtWidgets.QLabel("Input colour space", self)
        self.layout.addWidget(self.colSpcL)

        self.colSpcBox = QtWidgets.QComboBox(self)
        self.layout.addWidget(self.colSpcBox)
        for cs in nuke.getOcioColorSpaces():

            self.colSpcBox.addItem(cs.split("\t")[0])
        
        self.invertBox = QtWidgets.QCheckBox("Invert colour transform", self)
        self.layout.addWidget(self.invertBox)        
        
        self.aovL = QtWidgets.QLabel("AOVs", self)
        self.layout.addWidget(self.aovL)
        
        self.aovBox = QtWidgets.QListView(self)
        self.aovBoxModel = AovListModel()
        self.aovBoxSel = QtCore.QItemSelectionModel(self.aovBoxModel)
        
        self.aovBox.setModel(self.aovBoxModel)
        self.aovBox.setSelectionModel(self.aovBoxSel)
        self.aovBox.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.aovBox.setMinimumHeight(300)
        self.layout.addWidget(self.aovBox)
        
        self.aovBtnsLayout = QtWidgets.QHBoxLayout(self)
        
        self.aovAddBtn = QtWidgets.QPushButton("Add", self)
        self.aovAddBtn.clicked.connect(self.addAov)
        
        self.aovTypeBox = QtWidgets.QComboBox(self)

        self.aovRmBtn = QtWidgets.QPushButton("Remove", self)
        self.aovRmBtn.clicked.connect(self.rmAov)

        self.aovBtnsLayout.addWidget(self.aovAddBtn)
        self.aovBtnsLayout.addWidget(self.aovTypeBox)
        self.aovBtnsLayout.addWidget(self.aovRmBtn)
        self.layout.addLayout(self.aovBtnsLayout)

        self.button = QtWidgets.QPushButton("Create Read", self)
        self.button.clicked.connect(self.createRead)
        self.layout.addWidget(self.button)
        
        self.layout.addStretch()

    def addAov(self):
        
        if self.aovTypeBox.count() > 0:
            
            self.aovBoxModel.appendRow(QtGui.QStandardItem(self.aovTypeBox.currentText()))
    
    def rmAov(self):
        
        selection = self.aovBoxSel.selectedIndexes()
        removeList = []
        for index in selection:
            
            removeList.append(self.aovBoxModel.itemFromIndex(index))
            
        for item in removeList:
            
            self.aovBoxModel.removeRow(item.row())
        
        
    def chooseFile(self):
        
        self.pathField.setText(QtWidgets.QFileDialog.getOpenFileName()[0])
        
        readTmp = nuke.nodes.Read(file=self.pathField.text(), colorspace="Raw")
        
        self.aovTypeBox.clear()
        layers = nuke.layers(readTmp)
        for layer in layers:
            
            self.aovTypeBox.addItem(layer)

        nuke.delete(readTmp)

    def createRead(self):
        
        viewer = nuke.activeViewer().node()
        
        finalTransform = 0

        if self.invertBox.isChecked():
            
            process = nuke.ViewerProcess.node(viewer["viewerProcess"].value())

            read = nuke.nodes.Read(file=self.pathField.text(), colorspace="Raw")
            ocio = nuke.nodes.OCIODisplay(colorspace=self.colSpcBox.currentText(), invert=True, display=process["display"].value(), view=process["view"].value())
            ocio.setInput(0, read)
            finalTransform = ocio
        
        else:
            
            read = nuke.nodes.Read(file=self.pathField.text(), colorspace=self.colSpcBox.currentText())
            finalTransform = read
            
        for aov in self.aovBoxModel.aovList:
            
            shuffle = nuke.nodes.Shuffle2(in1 = aov.text())
            shuffle.setInput(0, finalTransform)

window = Window()
window.show()