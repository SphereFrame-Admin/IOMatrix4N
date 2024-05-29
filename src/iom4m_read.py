from PySide2 import QtCore, QtGui, QtWidgets

class Window(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowFlags(QtGui.Qt.WindowStaysOnTopHint)
        self.resize(300, 100)
        self.setWindowTitle("Read Media (IOMatrix)")
        
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
        
        self.invertBox = QtWidgets.QCheckBox("Invert colour transform", self)
        self.layout.addWidget(self.invertBox)        

        for cs in nuke.getOcioColorSpaces():

            self.colSpcBox.addItem(cs.split("\t")[0])
        
        self.button = QtWidgets.QPushButton("Create Read", self)
        self.button.clicked.connect(self.createRead)
        self.layout.addWidget(self.button)
        
        self.layout.addStretch()

    def chooseFile(self):
        
        self.pathField.setText(QtWidgets.QFileDialog.getOpenFileName()[0])

    def createRead(self):
        
        viewer = nuke.activeViewer().node()
        
        if self.invertBox.isChecked():
            
            process = nuke.ViewerProcess.node(viewer["viewerProcess"].value())

            read = nuke.nodes.Read(file=self.pathField.text(), colorspace="Raw")
            ocio = nuke.nodes.OCIODisplay(colorspace=self.colSpcBox.currentText(), invert=True, display=process["display"].value(), view=process["view"].value())
            ocio.setInput(0, read)
            viewer.setInput(0, ocio)
            return

        read = nuke.nodes.Read(file=self.pathField.text(), colorspace=self.colSpcBox.currentText())
        viewer.setInput(0, read)

window = Window()
window.show()