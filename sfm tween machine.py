# -*- coding: utf-8 -*-
#SFM TweenMachine v.1.0.1"
#BY http://steamcommunity.com/id/OMGTheresABearInMyOatmeal/
#feel free to modify the script for your own use
# Created: Tue Apr  9 20:00:35 2019


from PySide import QtCore, QtGui, shiboken
from PySide.QtCore import QObject, Signal, Slot
import sfmUtils,sfm,sfmApp,vs
from vs import g_pDataModel as dm

class tween_MainWindow(QtGui.QMainWindow):
    ToggleOvershoot = Signal(bool)
    def __init__(self):
        super(tween_MainWindow, self).__init__()
	self.isdocked=False
        self.MainWindow = QtGui.QMainWindow()
        self.MainWindow.installEventFilter(self)
        self.MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.controlListCache=None#only used to see if selection changed
        self.controlListLive=sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList
	self.allenabledcontrols={}
	
	
        self.setupUi(self.MainWindow)
        self.MainWindow.show()        
	self.centralwidget.installEventFilter(self)
	
	
	
    def add_or_remove_activeControls(self,checkbox,keyname,keyvalue):
	
	
	if not checkbox.isChecked():
	    self.allenabledcontrols.pop(keyname)
	else:
	    self.allenabledcontrols[keyname]=keyvalue
	    
	    
	#only gets called if selection changed 
    def addAllControls(self):
	
	#newcount=self.controlListLive.count()
	
	
	currentcount=self.verticalLayout_2.count()-1	
	self.allenabledcontrols.clear()
	
	for i in range(currentcount):#deletes all the current controls
	    self.verticalLayout_2.itemAt(i).widget().deleteLater()	
	
	for activeControl in self.controlListLive:
	    self.allenabledcontrols[activeControl.GetName()]=activeControl
	    SelectedControls=self.TemplateControlPageWidget(activeControl.GetName(),self.scrollAreaWidgetContents)
	    self.verticalLayout_2.insertWidget(0,SelectedControls)    
	    
	    
	    SelectedControls.checkEnable.clicked.connect(lambda check=SelectedControls.checkEnable,name=activeControl.GetName(),value=activeControl:self.add_or_remove_activeControls(check,name,value))
	    self.ToggleOvershoot.connect(SelectedControls.overshoot)	
	    
	    self.toggle_all.triggered.connect(SelectedControls.togglechecked)
	    SelectedControls.spinBox.valueChanged.connect(lambda lerpvalue=self.allSelectedControls.spinBox.value(),control=activeControl:self.OnControlSliderMove(control,lerpvalue))
	    
	    SelectedControls.overshoot(self.actionAllow_overshoot.isChecked())
	
    def windowHasGainFocus(self):
	#everytime the window gains focus and selection gets changed it reupdates the control list
        sfmApp.SetTimelineMode(4)
        if self.controlListCache and self.iscontrolListDirty():
            self.controlListCache=list(sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList)
            self.addAllControls()
        elif not self.controlListCache: 
            
            self.controlListCache=list(sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList)
            self.addAllControls()
            
            
            
    def iscontrolListDirty(self):
        
        if self.controlListLive.count() != len(self.controlListCache):#diff size
            
            return True
        
        for i in range(self.controlListLive.count()):
           
            if self.controlListLive[i].GetId().__int__() != self.controlListCache[i].GetId().__int__():
                
                return True
        
        
        
        
        return False
    
    
    
    def eventFilter(self, obj, event):
        
        if event.type() == QtCore.QEvent.WindowActivate or event.type() == QtCore.QEvent.FocusIn or (self.isdocked and event.type() == QtCore.QEvent.Enter):
            
            self.windowHasGainFocus()
            
        if event.type() == QtCore.QEvent.Close:
	    if not dm.IsUndoEnabled():
		dm.SetUndoEnabled(True) #just incase undo is off when closing

        return super(QtGui.QMainWindow, self).eventFilter(obj, event)
    
    def dock_to_sfm(self):
	
	sfmApp.RegisterTabWindow("tween_MainWindow", "SFM TweenMachine", shiboken.getCppPointer(self.centralwidget)[0])
	sfmApp.ShowTabWindow("tween_MainWindow")  	
	self.MainWindow.hide()
	self.isdocked=True
	
    def toggle_stay_on_top(self,bol):
        
        if bol:
            # enabled
            self.MainWindow.setWindowFlags(self.MainWindow.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            # disable
            self.MainWindow.setWindowFlags(self.MainWindow.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        # re-show the window after changing flags
        self.MainWindow.show()
    
    
    def GetChannels(self,control):
        
        if control.GetTypeString()=='DmElement':
            
            if control.HasAttribute("rightvaluechannel"):
                return control.rightvaluechannel,control.leftvaluechannel
            else:
                return control.channel,None
            
        elif control.GetTypeString()=='DmeTransformControl':
  
            return control.positionChannel,control.orientationChannel    
        
        
    def get_current_shot_from_frame(self,frame):
	
	return sfmApp.GetMovie().FindOrCreateFilmTrack().FindFilmClipAtTime(self.get_keytime_from_playhead())
    
	#vs.movieobjects.FindAnimationSetForDag(sfmApp.GetDocumentRoot().settings.graphEditorState.activeControlList[0].GetDag())
	
    def get_keytime_from_playhead(self):
	
	return vs.DmeTime_t( ((1.0/sfmApp.GetFramesPerSecond())*sfmApp.GetHeadTimeInFrames()))
	
	
    def get_keytime_from_frame(self,frame):
	#frame 0 is at vs.DmeTime_t(5.0)
	
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
            bookmarkslist=Channel.log.bookmarksX#for x,y,z axis
        else:
            bookmarkslist=Channel.log.bookmarks#for floats
            
            
            
        # check for existing key first    
            
            
        index=0
        for keytime in bookmarkslist:
            
            if time==keytime and  index+1<Channel.log.GetNumBookmarks(0):#if already bookmarked
                return bookmarkslist[index-1],bookmarkslist[index+1] 
            

            if time > keytime and index+1<Channel.log.GetNumBookmarks(0) and time < bookmarkslist[index+1]:#find the two bookmarks that the new time is in between
                return keytime,bookmarkslist[index+1]               
            index+=1        
            
        return None ,None #didnt find them
    
    
    
    def lerpKey(self,log,time,leftkeytime,rightkeytime,lerpAmount):
        
        
        
        if log.FindKeyWithinTolerance(leftkeytime,vs.DmeTime_t(10))  < 0 or log.FindKeyWithinTolerance(rightkeytime,vs.DmeTime_t(10)) < 0 :
	    #this insures that the keyframe exist
	    log.InsertKeyAtTime(leftkeytime)
	    log.InsertKeyAtTime(rightkeytime)
            
       # print leftkeytime,rightkeytime
        
        #gets key value at bookmark time
        leftkeyvalue=log.GetKeyValue(log.FindKey(leftkeytime))
        
        rightkeyvalue=log.GetKeyValue(log.FindKey(rightkeytime))
	
        
        
	
        #add new bookmark at playhead
        self.addBookmark(log,time)
        
       
        #calulate lerp Value dependent on type
        if log.GetTypeString()=='DmeVector3Log':
            
        
            lerpValue=vs.mathlib.VectorLerp(leftkeyvalue,rightkeyvalue,lerpAmount)
           
        elif log.GetTypeString()=='DmeQuaternionLog':
            lerpValue=vs.Quaternion().Identity()
            vs.mathlib.QuaternionSlerp(leftkeyvalue,rightkeyvalue,lerpAmount,lerpValue)
        
        elif log.GetTypeString()=='DmeFloatLog':

            lerpValue=((1-lerpAmount)*leftkeyvalue)+(lerpAmount * rightkeyvalue)
            
        
        
        #makes step key
	#three part process
	#1.insert a key right before the actual keyframe with the value of the left side bookmark key value
	#2.next add the new keyframe with new value
	#3.then change the next key value to the same as the new value
        log.InsertKey(time-vs.DmeTime_t(1),leftkeyvalue)
        index=log.InsertKey(time,lerpValue)	      
        log.GetLayer(0).values[index+1]=lerpValue
        
        
        
         
         
         
         

         
         
         
         
    def OnAllSliderMove(self,lerpValue):
       # playheadframe= self.get_keytime_from_frame(sfmApp.GetHeadTimeInFrames())
        
        dm.SetUndoEnabled(False)#important must temp disable undo system to edit sfm memory in real time else sfm will crash
	#the better option would be to add the changes to the undo system but there is little doc about how to do it
	# in the vs lib 
	
	
	
        for activeControl in self.controlListLive:#loop thur all selected controls
            
            
            
            if activeControl.GetName() not in self.allenabledcontrols.keys():#if its unchecked skip it
		
		continue
            
            
            
            FirstChannel,SecondChannel =self.GetChannels(activeControl)        
        
            if FirstChannel.log.GetNumBookmarks(0)>1:
                
                leftbook,rightbook= self.get_before_and_after_keys(FirstChannel,FirstChannel.GetCurrentTime())
                
                if not leftbook or not rightbook:
		    self.statusbar.showMessage('one or more controls are missing bookmarks around the playhead' ,2000)
    
                    print   activeControl.GetName()+' is missing bookmarks around the playhead'
		   
                    continue
                

                self.lerpKey(FirstChannel.log,FirstChannel.GetCurrentTime(),leftbook,rightbook,lerpValue)

                
            if SecondChannel and SecondChannel.log.GetNumBookmarks(0)>1:
                
                leftbook,rightbook= self.get_before_and_after_keys(SecondChannel,SecondChannel.GetCurrentTime())
                
                if not leftbook or not rightbook:
		    self.statusbar.showMessage('one or more controls are missing bookmarks around the playhead' ,2000)
    
                    print   activeControl.GetName()+' is missing bookmarks around the playhead'
                    continue
                

                self.lerpKey(SecondChannel.log,SecondChannel.GetCurrentTime(),leftbook,rightbook,lerpValue)



	#do this to update viewport in realtime
        sfmApp.SetHeadTimeInFrames(sfmApp.GetHeadTimeInFrames())
        dm.SetUndoEnabled(True) 
        
        
        

    
    
    
    def OnControlSliderMove(self,Control,lerpValue):#for individual sliders
	playheadframe= self.get_keytime_from_frame(sfmApp.GetHeadTimeInFrames())
	#sfm.SetOperationMode( "Record" )
	
	
	for elm in self.controlListLive:
	    if elm.GetId().__int__()==Control.GetId().__int__():
		activeControl=elm
		break
	    
	    
	dm.SetUndoEnabled(False)#important must temp disable undo system to edit sfm memory in real time else sfm will crash
   
	    
	    
	FirstChannel,SecondChannel =self.GetChannels(activeControl)        
    
	if FirstChannel.log.GetNumBookmarks(0)>1:
	    
	    leftbook,rightbook= self.get_before_and_after_keys(FirstChannel,playheadframe)
	    
	    if not leftbook or not rightbook:
		print   activeControl.GetName()+' book error'
	       
		return
	    

	    self.lerpKey(FirstChannel.log,playheadframe,leftbook,rightbook,lerpValue)
	else:
	    self.statusbar.showMessage('need more keys',2000)
	    
	if SecondChannel and SecondChannel.log.GetNumBookmarks(0)>1:
	    
	    leftbook,rightbook= self.get_before_and_after_keys(SecondChannel,playheadframe)
	    
	    if not leftbook or not rightbook:
		print 'book error'
		
		return
	    

	    self.lerpKey(SecondChannel.log,playheadframe,leftbook,rightbook,lerpValue)



		
	sfmApp.SetHeadTimeInFrames(sfmApp.GetHeadTimeInFrames())
	dm.SetUndoEnabled(True) 
	
	
 	
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(600, 100)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(580, 0))
        MainWindow.setMaximumSize(QtCore.QSize(800, 16777215))
        
        MainWindow.setAnimated(False)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
	self.centralwidget.setFocusPolicy(QtCore.Qt.ClickFocus )
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





        self.allSelectedControls=self.TemplateControlPageWidget("All Selected",self.scrollAreaWidgetContents)
	self.allSelectedControls.horizontalLayout.setContentsMargins(9, -1, 0, 20) 
        self.verticalLayout_3.addWidget(self.allSelectedControls)        
        self.ToggleOvershoot.connect(self.allSelectedControls.overshoot)
        

        spacerItem1 = QtGui.QSpacerItem(20, 90, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)

	#self.scrollArea.setFrameStyle(QtGui.QFrame.NoFrame)
	self.scrollArea.hide()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 630, 21))
        self.menubar.setObjectName("menubar")
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setTearOffEnabled(False)
        self.menuOptions.setTitle("options")
        self.menuOptions.setSeparatorsCollapsible(True)
	
        self.windowOptions = QtGui.QMenu(self.menubar)
        self.windowOptions.setTitle("window")
        
        
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
        
        self.actionAllways_on_top = QtGui.QAction(MainWindow)
        self.actionAllways_on_top.setCheckable(True)        
        self.actionAllways_on_top.setText('Always On Top')
        self.actionAllways_on_top.setChecked(True)
	
        self.windowOptions.addAction(self.actionAllways_on_top)
	
        self.menuOptions.addAction(self.actionShow_all_selected)
        self.menuOptions.addAction(self.actionAllow_overshoot)
        self.menubar.addAction(self.menuOptions.menuAction())
	self.menubar.addAction(self.windowOptions.menuAction())
	self.centralwidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
	
	self.centralwidget.addAction(self.actionShow_all_selected)
	self.centralwidget.addAction(self.actionAllow_overshoot)
	
	self.toggle_all = QtGui.QAction(MainWindow)	        
	self.toggle_all.setText('Toggle All')
	
	self.dock_window = QtGui.QAction(MainWindow)	        
	self.dock_window.setText('Dock Window')	
	
	
	
	self.windowOptions.addAction(self.dock_window)
	self.centralwidget.addAction(self.toggle_all)
	
	
	
	self.dock_window.triggered.connect(self.dock_to_sfm)
        QtCore.QObject.connect(self.actionAllways_on_top, QtCore.SIGNAL("toggled(bool)"), self.toggle_stay_on_top)
       # QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL("valueChanged(int)"), lambda:self.spinBox.setValue(self.horizontalSlider.value()/100.0))
        QtCore.QObject.connect(self.actionAllow_overshoot, QtCore.SIGNAL("toggled(bool)"), lambda:self.ToggleOvershoot.emit(self.actionAllow_overshoot.isChecked()))
        #QtCore.QObject.connect(self.actionShow_all_selected, QtCore.SIGNAL("toggled(bool)"), self.showAllcontrols)

	self.actionShow_all_selected.toggled.connect(self.scrollArea.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.retranslateUi(MainWindow)
        self.allSelectedControls.spinBox.valueChanged.connect(lambda:self.OnAllSliderMove(self.allSelectedControls.spinBox.value()))
        
        
       # sfmApp.RegisterTabWindow("centralwidget", "Python Console", shiboken.getCppPointer(self.centralwidget)[0])
       # sfmApp.ShowTabWindow("centralwidget")    
       

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "SFM TweenMachine v.1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Controls", None, QtGui.QApplication.UnicodeUTF8))
        #self.checkEnable.setText(QtGui.QApplication.translate("MainWindow", "All Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_all_selected.setText(QtGui.QApplication.translate("MainWindow", "Show All Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAllow_overshoot.setText(QtGui.QApplication.translate("MainWindow", "Allow Overshoot", None, QtGui.QApplication.UnicodeUTF8))

	#custom QWidget for control page
    class TemplateControlPageWidget(QtGui.QWidget):
    
    
	def __init__(self,controlName,parentwidget=None):
	    super(self.__class__, self).__init__(parentwidget)
	    self.parentwidget = parentwidget
    
	    self.Setupwidget(controlName)
	   
    
	    
	def overshoot(self,bol):
	    if bol:
		self.horizontalSlider.setMinimum(-50)
		self.horizontalSlider.setMaximum(150)
	    else:
		self.horizontalSlider.setMinimum(0)
		self.horizontalSlider.setMaximum(100)    
		
	def togglechecked(self):
	    self.checkEnable.click()
	    

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
	    self.label.setMinimumSize(QtCore.QSize(100, 0))
	    self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	    self.label.setText(controlName)
	    self.label.setFixedWidth(120)
	    #self.label.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction |QtCore.Qt.TextSelectableByMouse);
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



