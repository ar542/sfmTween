# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/AR/Documents/GitHub/sfmTween/sfmtween.ui'
#
# Created: Tue Apr  9 20:00:35 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
from PySide.QtCore import QObject, Signal, Slot
import sfmUtils,sfm,sfmClipEditor,sfmApp,vs
from vs import g_pDataModel as dm
class tween_MainWindow(QtGui.QMainWindow):
    ToggleOvershoot = Signal(bool)
    def __init__(self):
        super(tween_MainWindow, self).__init__()
        self.MainWindow = QtGui.QMainWindow()
        self.MainWindow.installEventFilter(self)
        self.MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.controlListCache=None#only used to see if selection changed
        self.controlListLive=sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList
        self.setupUi(self.MainWindow)
        self.MainWindow.show()
        
	
    def windowHasGainFocus(self):
        sfmApp.SetTimelineMode(4)
        if self.controlListCache and self.iscontrolListDirty():
            self.controlListCache=list(sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList)
            
        elif not self.controlListCache: 
            
            self.controlListCache=list(sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList)
            
            
            
            
    def iscontrolListDirty(self):
        
        if self.controlListLive.count() != len(self.controlListCache):#diff size
            
            return True
        
        for i in range(self.controlListLive.count()):
           
            if self.controlListLive[i].GetId().__int__() != self.controlListCache[i].GetId().__int__():
                
                return True
        
        
        
        
        return False
    
    
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.windowHasGainFocus()
            
            

        return super(QtGui.QMainWindow, self).eventFilter(obj, event)
    
    
    
    def GetChannels(self,control):
        
        if control.GetTypeString()=='DmElement':
            
            if control.HasAttribute("rightvaluechannel"):
                return control.rightvaluechannel,control.leftvaluechannel
            else:
                return control.channel,None
            
        elif control.GetTypeString()=='DmeTransformControl':
  
            return control.positionChannel,control.orientationChannel    
        
        
        
    def get_keytime_from_frame(self,frame):

        return vs.DmeTime_t( ((1.0/sfmApp.GetFramesPerSecond())*frame)+5.0)
        
    def addBookmark(self,log,time):
        #time is DmeTime_t type
        if log.GetNumBookmarkComponents()>1:
            
            log.AddBookmark(time,0)
            log.AddBookmark(time,1)
            log.AddBookmark(time,2)
            
        else:
            log.AddBookmark(time,0)
        
    def get_before_and_after_keys(self,Channel,time):# get the prev and next bookmark key time where the headtime is



        if Channel.log.GetNumBookmarkComponents()>1:
            bookmarkslist=Channel.log.bookmarksX
        else:
            bookmarkslist=Channel.log.bookmarks
            
        # check for existing key first    
            
            
        index=0
        for keytime in bookmarkslist:
            
            if time==keytime and  index+1<Channel.log.GetNumBookmarks(0):
                return bookmarkslist[index-1],bookmarkslist[index+1] 
            

            if time > keytime and index+1<Channel.log.GetNumBookmarks(0) and time < bookmarkslist[index+1]:
                
                return keytime,bookmarkslist[index+1]              
                
            index+=1        
            
        return None ,None
    
    def lerpKey(self,log,time,leftkeyvalue,rightkeyvalue,lerpAmount):
        
        lerpValue=vs.mathlib.VectorLerp(leftkeyvalue,rightkeyvalue,lerpAmount)
        log.FindOrAddKey(time,vs.DmeTime_t(1.0),lerpValue)
        
        print time,lerpValue
         
    def OnSliderMove(self,lerpValue):
        playheadframe= self.get_keytime_from_frame(sfmApp.GetHeadTimeInFrames())
        #sfm.SetOperationMode( "Record" )
        for activeControl in self.controlListLive:
            
            
            FirstChannel,SecondChannel =self.GetChannels(activeControl)        
        
            if FirstChannel.log.GetNumBookmarks(0)>1:
                
                leftbook,rightbook= self.get_before_and_after_keys(FirstChannel,playheadframe)
                
                if not leftbook or not rightbook:
                    print 'book error'
                    return
                
                dm.SetUndoEnabled(False)
                #place code here
                
                #self.addBookmark(FirstChannel.log,playheadframe)
                print leftbook,rightbook
                self.lerpKey(FirstChannel.log,playheadframe,FirstChannel.log.GetValue(leftbook),FirstChannel.log.GetValue(rightbook),lerpValue)
                dm.SetUndoEnabled(True)  

                
                
                
            else:
                self.statusbar.showMessage('need more keys',2000)
        sfmApp.SetHeadTimeInFrames(sfmApp.GetHeadTimeInFrames())
        
    def showAllcontrols(self,bol):
        #change to hide
        if bol:
            #make own func
            for i in range(6):
                self.allSelectedControls=TemplateControlPageWidget("all seflected",self.scrollAreaWidgetContents)
                self.verticalLayout_2.insertWidget(1,self.allSelectedControls)        
                self.ToggleOvershoot.connect(self.allSelectedControls.overshoot)        
        else:
            count=self.verticalLayout_2.count()-1
            for i in range(1,count):
                self.verticalLayout_2.itemAt(i).widget().deleteLater()
        
        
    
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(600, 333)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(580, 0))
        MainWindow.setMaximumSize(QtCore.QSize(600, 16777215))
       # MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        MainWindow.setAnimated(False)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea = QtGui.QScrollArea(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 590, 179))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")





        self.allSelectedControls=TemplateControlPageWidget("all selected",self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.allSelectedControls)        
        self.ToggleOvershoot.connect(self.allSelectedControls.overshoot)
        

        spacerItem1 = QtGui.QSpacerItem(20, 90, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)



        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 630, 21))
        self.menubar.setObjectName("menubar")
        self.menuOpsions = QtGui.QMenu(self.menubar)
        self.menuOpsions.setTearOffEnabled(False)
        self.menuOpsions.setTitle("opions")
        self.menuOpsions.setSeparatorsCollapsible(True)
        self.menuOpsions.setObjectName("menuOpsions")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionShow_all_selected = QtGui.QAction(MainWindow)
        self.actionShow_all_selected.setCheckable(True)
        self.actionShow_all_selected.setObjectName("actionShow_all_selected")
        self.actionAllow_overshoot = QtGui.QAction(MainWindow)
        self.actionAllow_overshoot.setCheckable(True)
        self.actionAllow_overshoot.setObjectName("actionAllow_overshoot")
        self.menuOpsions.addAction(self.actionShow_all_selected)
        self.menuOpsions.addAction(self.actionAllow_overshoot)
        self.menubar.addAction(self.menuOpsions.menuAction())


       # QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL("valueChanged(int)"), lambda:self.spinBox.setValue(self.horizontalSlider.value()/100.0))
        QtCore.QObject.connect(self.actionAllow_overshoot, QtCore.SIGNAL("toggled(bool)"), lambda:self.ToggleOvershoot.emit(self.actionAllow_overshoot.isChecked()))
        QtCore.QObject.connect(self.actionShow_all_selected, QtCore.SIGNAL("toggled(bool)"), lambda:self.showAllcontrols(self.actionShow_all_selected.isChecked()))


        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.retranslateUi(MainWindow)
        self.allSelectedControls.spinBox.valueChanged.connect(lambda:self.OnSliderMove(self.allSelectedControls.spinBox.value()))
        

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "selected", None, QtGui.QApplication.UnicodeUTF8))
        #self.checkEnable.setText(QtGui.QApplication.translate("MainWindow", "All Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_all_selected.setText(QtGui.QApplication.translate("MainWindow", "show all selected", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAllow_overshoot.setText(QtGui.QApplication.translate("MainWindow", "allow overshoot", None, QtGui.QApplication.UnicodeUTF8))

    #custom QWidget for control page
class TemplateControlPageWidget(QtGui.QWidget):


    def __init__(self,controlName,parentwidget=None):
        super(TemplateControlPageWidget, self).__init__(parentwidget)
        self.parentwidget = parentwidget

        self.Setupwidget(controlName)
       

        
    def overshoot(self,bol):
        if bol:
            self.horizontalSlider.setMinimum(-50)
            self.horizontalSlider.setMaximum(150)
        else:
            self.horizontalSlider.setMinimum(0)
            self.horizontalSlider.setMaximum(100)            
        
    def Setupwidget(self,controlName):    
       
       
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.setLayout(self.horizontalLayout)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, -1, 0, 20)       
        self.checkEnable = QtGui.QCheckBox(self.parentwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkEnable.sizePolicy().hasHeightForWidth())
        self.checkEnable.setSizePolicy(sizePolicy)
        self.checkEnable.setChecked(True)
        self.horizontalLayout.addWidget(self.checkEnable)
        self.label = QtGui.QLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(120, 0))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setText(controlName)
        
        self.horizontalLayout.addWidget(self.label)
        
        
        self.spinBox = QtGui.QDoubleSpinBox(self.parentwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
        self.spinBox.setSizePolicy(sizePolicy)
        self.spinBox.setFrame(True)
        self.spinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.spinBox.setReadOnly(True)
        self.spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.spinBox.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
        self.spinBox.setMinimum(-.5)
        self.spinBox.setMaximum(1.5)
        self.spinBox.setValue(.50)
        self.horizontalLayout.addWidget(self.spinBox)
        self.horizontalSlider = QtGui.QSlider(self.parentwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider.sizePolicy().hasHeightForWidth())
        self.horizontalSlider.setSizePolicy(sizePolicy)
        self.horizontalSlider.setMinimumSize(QtCore.QSize(300, 0))
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setValue(50)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(25)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalLayout.addWidget(self.horizontalSlider)
        spacerItem = QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout.addItem(spacerItem)
        
        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL("valueChanged(int)"), lambda:self.spinBox.setValue(self.horizontalSlider.value()/100.0))
        QtCore.QObject.connect(self.checkEnable, QtCore.SIGNAL("toggled(bool)"), self.horizontalSlider.setEnabled)



MainWindow = tween_MainWindow()



