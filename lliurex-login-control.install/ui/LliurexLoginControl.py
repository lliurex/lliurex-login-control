#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex,QUrl
from PySide6.QtGui import QDesktopServices
import os
import signal
import copy
import time
import N4dManager

signal.signal(signal.SIGINT, signal.SIG_DFL)

SAVE_DATA=30
RESTORE_DATA=31

class GatherInfo(QThread):

	infoGathered=Signal(dict)

	def __init__(self,manager):

		super().__init__()
		self.manager=manager
	
	#def __init__
		
	def run(self,*args):
		
		time.sleep(0.2)
		ret=self.manager.loadConfig()
		self.infoGathered.emit(ret)

	#def run

#class GatherInfo

class UpdateInfo(QThread):

	infoUpdated=Signal(dict)

	def __init__(self,manager,info, confirmPasswordEntry):

		super().__init__()
		self.manager=manager
		self.updateInfo=info
		self.confirmPasswordEntry=confirmPasswordEntry

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		ret=self.manager.applyChanges(self.updateInfo,self.confirmPasswordEntry)
		self.infoUpdated.emit(ret)
	
	#def run

#class UpdateInfo

class LliurexLoginControl(QObject):

	currentStackChanged=Signal()
	currentOptionsStackChanged=Signal()
	showSpinnerChanged=Signal()
	isWifiEnabledChanged=Signal()
	currentLoginOptionChanged=Signal()
	currentPasswordChanged=Signal()
	passwordEntryEnabledChanged=Signal()
	showEditPasswordBtnChanged=Signal()
	showConfirmPasswordChanged=Signal()
	showClearPasswordBtnChanged=Signal()
	isGuestUserEnabledChanged=Signal()
	changesInLoginSettingsChanged=Signal()
	showSettingsMessageChanged=Signal()
	showChangesDialogChanged=Signal()
	showCDCWarningChanged=Signal()
	showPopUpChanged=Signal()
	closeGuiChanged=Signal()

	def __init__(self,ticket=None):

		super().__init__()
		self.initBridge(ticket)

	#def __init__

	@Property(int,notify=currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack

	@currentStack.setter
	def currentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.currentStackChanged.emit()

	#def currentStack

	@Property(int, notify=currentOptionsStackChanged)
	def currentOptionsStack(self):

		return self._currentOptionsStack

	#def currentOptionsStack

	@currentOptionsStack.setter
	def currentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.currentOptionsStackChanged.emit()

	#def currentOptionsStack

	@Property(bool,notify=showSpinnerChanged)
	def showSpinner(self):

		return self._showSpinner

	#def showSpinner

	@showSpinner.setter
	def showSpinner(self,showSpinner):

		if self._showSpinner!=showSpinner:
			self._showSpinner=showSpinner
			self.showSpinnerChanged.emit()

	#def showSpinner

	@Property(bool,notify=isWifiEnabledChanged)
	def isWifiEnabled(self):

		return self._isWifiEnabled

	#def isWifiEnabled

	@isWifiEnabled.setter
	def isWifiEnabled(self,isWifiEnabled):

		if self._isWifiEnabled!=isWifiEnabled:
			self._isWifiEnabled=isWifiEnabled
			self.isWifiEnabledChanged.emit()

	#def isWifiEnabled

	@Property(int,notify=currentLoginOptionChanged)
	def currentLoginOption(self):

		return self._currentLoginOption

	#def currentLoginOption

	@currentLoginOption.setter
	def currentLoginOption(self,currentLoginOption):

		if self._currentLoginOption!=currentLoginOption:
			self._currentLoginOption=currentLoginOption
			self.currentLoginOptionChanged.emit()

	#def currentLoginOption

	@Property(str,notify=currentPasswordChanged)
	def currentPassword(self):

		return self._currentPassword

	#def currentPassword

	@currentPassword.setter
	def currentPassword(self,currentPassword):

		if self._currentPassword!=currentPassword:
			self._currentPassword=currentPassword
			self.currentPasswordChanged.emit()

	#def currentPassword

	@Property(bool,notify=passwordEntryEnabledChanged)
	def passwordEntryEnabled(self):

		return self._passwordEntryEnabled

	#def passwordEntryEnabled

	@passwordEntryEnabled.setter
	def passwordEntryEnabled(self,passwordEntryEnabled):

		if self._passwordEntryEnabled!=passwordEntryEnabled:
			self._passwordEntryEnabled=passwordEntryEnabled
			self.passwordEntryEnabledChanged.emit()

	#def passwordEntryEnabled

	@Property(bool,notify=showEditPasswordBtnChanged)
	def showEditPasswordBtn(self):

		return self._showEditPasswordBtn

	#def showEditPasswordBtn

	@showEditPasswordBtn.setter
	def showEditPasswordBtn(self,showEditPasswordBtn):

		if self._showEditPasswordBtn!=showEditPasswordBtn:
			self._showEditPasswordBtn=showEditPasswordBtn
			self.showEditPasswordBtnChanged.emit()

	#def showEditPasswordBtn

	@Property(bool,notify=showConfirmPasswordChanged)
	def showConfirmPassword(self):

		return self._showConfirmPassword

	#def showConfirmPassword

	@showConfirmPassword.setter
	def showConfirmPassword(self,showConfirmPassword):

		if self._showConfirmPassword!=showConfirmPassword:
			self._showConfirmPassword=showConfirmPassword
			self.showConfirmPasswordChanged.emit()

	#def showConfirmPassword

	@Property(bool,notify=showClearPasswordBtnChanged)
	def showClearPasswordBtn(self):

		return self._showClearPasswordBtn

	#def showClearPasswordBtn

	@showClearPasswordBtn.setter
	def showClearPasswordBtn(self,showClearPasswordBtn):

		if self._showClearPasswordBtn!=showClearPasswordBtn:
			self._showClearPasswordBtn=showClearPasswordBtn
			self.showClearPasswordBtnChanged.emit()

	#def showClearPasswordBtn

	@Property(bool,notify=isGuestUserEnabledChanged)
	def isGuestUserEnabled(self):

		return self._isGuestUserEnabled

	#def isGuestUserEnabled

	@isGuestUserEnabled.setter
	def isGuestUserEnabled(self, isGuestUserEnabled):

		if self._isGuestUserEnabled!=isGuestUserEnabled:
			self._isGuestUserEnabled=isGuestUserEnabled
			self.isGuestUserEnabledChanged.emit()

	#def isGuestUserEnabled

	@Property(bool,notify=changesInLoginSettingsChanged)
	def changesInLoginSettings(self):

		return self._changesInLoginSettings

	#def changesInLoginSettings

	@changesInLoginSettings.setter
	def changesInLoginSettings(self,changesInLoginSettings):

		if self._changesInLoginSettings!=changesInLoginSettings:
			self._changesInLoginSettings=changesInLoginSettings
			self.changesInLoginSettingsChanged.emit()

	#def changesInLoginSettings

	@Property(dict,notify=showSettingsMessageChanged)
	def showSettingsMessage(self):

		return self._showSettingsMessage

	#def showSettingsMessage

	@showSettingsMessage.setter
	def showSettingsMessage(self,showSettingsMessage):

		if self._showSettingsMessage!=showSettingsMessage:
			self._showSettingsMessage=showSettingsMessage
			self.showSettingsMessageChanged.emit()

	#def showSettingsMessage

	@Property(bool,notify=showChangesDialogChanged)
	def showChangesDialog(self):

		return self._showChangesDialog

	#def showChangesDialog

	@showChangesDialog.setter
	def showChangesDialog(self,showChangesDialog):

		if self._showChangesDialog!=showChangesDialog:
			self._showChangesDialog=showChangesDialog
			self.showChangesDialogChanged.emit()

	#def showChangesDialog

	@Property(bool,notify=showCDCWarningChanged)
	def showCDCWarning(self):

		return self._showCDCWarning

	#def showCDCWarning

	@showCDCWarning.setter
	def showCDCWarning(self,showCDCWarning):

		if self._showCDCWarning!=showCDCWarning:
			self._showCDCWarning=showCDCWarning
			self.showCDCWarningChanged.emit()

	#def _showCDCWarning

	@Property(dict,notify=showPopUpChanged)
	def showPopUp(self):

		return self._showPopUp

	#def showPopUp	

	@showPopUp.setter
	def showPopUp(self,showPopUp):
		
		if self._showPopUp!=showPopUp:
			self._showPopUp=showPopUp		
			self.showPopUpChanged.emit()

	#def showPopUp

	@Property(bool, notify=closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.closeGuiChanged.emit()

	#def _closeGui

	def initBridge(self,ticket):

		self.n4dMan=N4dManager.N4dManager()
		self._changesInLoginSettings=False
		self._showSettingsMessage={"show":False,"msgCode":"","type":""}
		self._showChangesDialog=False
		self._closeGui=False
		self._showPopUp={"show":False,"msgCode":""}
		self._currentStack=0
		self._currentOptionsStack=0
		self._isWifiEnabled=False
		self._currentLoginOption=0
		self._currentPassword=""
		self._passwordEntryEnabled=False
		self._showConfirmPassword=False
		self._showEditPasswordBtn=False
		self._isGuestUserEnabled=False
		self._showSpinner=True
		self._showClearPasswordBtn=False
		self._showCDCWarning=False
		self.passwordCleared=False
		self.n4dMan.setServer(ticket)
		self.gatherInfoT=GatherInfo(self.n4dMan)
		self.gatherInfoT.start()
		self.gatherInfoT.infoGathered.connect(self._loadConfig)
		self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)

	#def initBridge

	@Slot(dict)
	def _loadConfig(self,ret):		

		if not ret.get("status"):
			if self.currentStack==0:
				self.showSpinner=False
			else:
				self.showSettingsMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}
		else:
			if ret.get("code"):
				self.showSettingsMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}
			self._loadVars()
			self.currentStack=1

	#def _loadConfig

	def _loadVars(self):

		self.isWifiEnabled=self.n4dMan.isWifiEnabled
		self.currentLoginOption=self.n4dMan.currentLoginOption
		self.currentPassword=self.n4dMan.currentPassword
		self.isGuestUserEnabled=self.n4dMan.isGuestUserEnabled
		self.currentLoginSettings=copy.deepcopy(self.n4dMan.currentLoginSettings)
		self.confirmPasswordEntry=""
		self.passwordEntryEnabled=False
		self.showClearPasswordBtn=False
		self.showEditPasswordBtn=False
		self.passwordCleared=False

		if self.isWifiEnabled and self.currentLoginOption in (self.n4dMan.WifiMode.AUTOLOGIN,self.n4dMan.WifiMode.EASYLOGIN):
			if not self.currentPassword:
				self.passwordEntryEnabled=True
				self.showConfirmPassword=True
			else:
				self.showEditPasswordBtn=True
		else:
			if self.isWifiEnabled and not self.n4dMan.getIntegrationCDCStatus():
				self.showSettingsMessage={"show":True,"msgCode":self.n4dMan.WARNING_CDC_ACTIVATION_REQUIRED,"type":self.n4dMan.KIRIGAMI_MSG_WARNING}

			self._manageClearPasswordBtn()

	#def _loadVars

	def _manageClearPasswordBtn(self):

		hasPassword=bool(self.currentPassword)
		notOption3OrDisabled=(self.currentLoginOption not in (N4dManager.N4dManager.WifiMode.AUTOLOGIN,N4dManager.N4dManager.WifiMode.EASYLOGIN) or not self.isWifiEnabled)
		
		self.showClearPasswordBtn=hasPassword and notOption3OrDisabled

	#def _manageClearPasswordBtn

	@Slot(bool)
	def manageWifiControl(self,value):

		self.showSettingsMessage={"show":False,"msgCode":"","type":""}
		if value!=self.isWifiEnabled:
			self.isWifiEnabled=value
			self.currentLoginSettings["isWifiEnabled"]=value

		if value:
			if self.currentLoginOption==self.n4dMan.WifiMode.EASYLOGINWIRED:
				newLoginOption=self.n4dMan.WifiMode.EASYLOGIN.value
			else:
				newLoginOption=self.n4dMan.WifiMode.ENABLE.value
		else:
			if self.currentLoginOption==self.n4dMan.WifiMode.EASYLOGIN:
				newLoginOption=self.n4dMan.WifiMode.EASYLOGINWIRED.value
			else:
				newLoginOption=self.n4dMan.WifiMode.DISABLE.value			

		if newLoginOption!=self.currentLoginOption:
			self.currentLoginOption=newLoginOption
			self.currentLoginSettings["currentLoginOption"]=newLoginOption
			
		self._manageChanges()
		self._undoChangesInPassword()
		self._manageClearPasswordBtn()
		
	#def manageWifiControl

	@Slot(int)
	def manageLoginOptions(self,value):

		self.showSettingsMessage={"show":False,"msgCode":"","type":""}

		if value!=self.currentLoginOption:
			self.currentLoginOption=value
			self.currentLoginSettings["currentLoginOption"]=value

		self._manageChanges()
		self._undoChangesInPassword()
		self._manageClearPasswordBtn()

	#def manageLoginOptions
	
	@Slot(dict)
	def changeInConfirmPasswordEntry(self,value):

		if self.passwordEntryEnabled:
			self.confirmPasswordEntry=value.get("confirmPassword")
	
	#def changeInConfirmPasswordEntry

	@Slot(dict)
	def changeInPasswordEntry(self,value):

		if value.get("password")!=self.currentPassword:
			self.currentPassword=value.get("password")
			self.currentLoginSettings["currentPassword"]=value.get("password")

		self._manageChanges()

	#def changeInPasswordEntry

	@Slot()
	def editPasswordBtn(self):

		if self.currentLoginOption in (N4dManager.N4dManager.WifiMode.AUTOLOGIN,N4dManager.N4dManager.WifiMode.EASYLOGIN):
			self.passwordEntryEnabled=not self.passwordEntryEnabled
			self.showConfirmPassword=not self.showConfirmPassword

		if not self.passwordEntryEnabled:
			self._undoChangesInPassword()

	#def editPasswordBtn

	@Slot(bool)
	def manageGuestUser(self,value):

		self.showSettingsMessage={"show":False,"msgCode":"","type":""}
		if value!=self.isGuestUserEnabled:
			self.isGuestUserEnabled=value
			self.currentLoginSettings["isGuestUserEnabled"]=value

		self._manageChanges()

		
	#def manageWifiControl

	def _manageChanges(self):

		if self.currentLoginSettings!=self.n4dMan.currentLoginSettings:
			self.changesInLoginSettings=True
		else:
			self.changesInLoginSettings=False
	
	#def _manageChanges

	def _undoChangesInPassword(self):

		self.showSettingsMessage={"show":False,"msgCode":"","type":""}

		if not self.passwordCleared or self.currentLoginOption in (N4dManager.N4dManager.WifiMode.AUTOLOGIN,N4dManager.N4dManager.WifiMode.EASYLOGIN):
			self.currentPassword=self.n4dMan.currentPassword
			self.currentLoginSettings["currentPassword"]=self.currentPassword
			self.confirmPasswordEntry=""
			self.passwordCleared=False

		if not self.isWifiEnabled or self.currentLoginOption not in (N4dManager.N4dManager.WifiMode.AUTOLOGIN,N4dManager.N4dManager.WifiMode.EASYLOGIN):
			self.passwordEntryEnabled=False
			self.showConfirmPassword=False
			self.showEditPasswordBtn=False
			return

		if not self.currentPassword:
			self.passwordEntryEnabled=True
			self.showConfirmPassword=True
		else:
			self.showEditPasswordBtn=True
			self.showConfirmPassword=False

	#def _undoChangesInPassword

	@Slot()
	def applyChanges(self):

		self.showSettingsMessage={"show":False,"msgCode":"","type":""}
		self.showPopUp={"show":True,"msgCode":SAVE_DATA}
		self.showChangesDialog=False
		self.updateInfoT=UpdateInfo(self.n4dMan,self.currentLoginSettings,self.confirmPasswordEntry)
		self.updateInfoT.start()
		self.updateInfoT.infoUpdated.connect(self._updateInfoRet)
		self.updateInfoT.finished.connect(self.updateInfoT.deleteLater)

	#def applyChanges	

	@Slot(dict)
	def _updateInfoRet(self,ret):

		self.showPopUp={"show":False,"msgCode":""}

		if not ret.get("status"):
			self.closeGui=False
			self.showSettingsMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}
			return

		self._initForm()
		self.showSettingsMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}

		isCDCMissign=self.isWifiEnabled and self.currentLoginOption not in (N4dManager.N4dManager.WifiMode.AUTOLOGIN,N4dManager.N4dManager.WifiMode.EASYLOGIN) and not self.n4dMan.getIntegrationCDCStatus()
		if isCDCMissign:
			self.showCDCWarning=True
		
		self.closeGui=True

	#def _updateInfoRet

	def _initForm(self):

		self._loadVars()
		self.changesInLoginSettings=False
		self.showConfirmPassword=False
		self.closeGui=True

	#def _initForm

	@Slot()
	def manageCDCWarning(self):

		self.showCDCWarning=False
		self.closeGui=True

	#def manageCDCWarning	

	@Slot()
	def cancelChanges(self):

		self.showPopUp={"show":True,"msgCode":RESTORE_DATA}
		self.showChangesDialog=False
		self.showSettingsMessage={"show":False,"msgCode":"","type":""}
		self._initForm()
		self.showPopUp={"show":False,"msgCode":""}

	#def cancelChanges

	@Slot(str)
	def manageChangesDialog(self,action):
		
		if action=="Accept":
			self.applyChanges()
		elif action=="Discard":
			self.cancelChanges()
		elif action=="Cancel":
			self.closeGui=False
			self.showChangesDialog=False

	#def manageChangesDialog

	@Slot()
	def clearPassword(self):

		self.showSettingsMessage={"show":False,"msgCode":"","type":""}
		self.currentPassword=""
		self.currentLoginSettings["currentPassword"]=""
		self.confirmPasswordEntry=""
		self.changeInPassword=True
		self.passwordCleared=True
		self.showClearPasswordBtn=False
		self._manageChanges()

	#def clearPassword

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack

	#def manageTransitions
	
	@Slot()
	def openHelp(self):
		
		helpUrl='https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Integración+con+las+WiFis+educativas+de+la+GVA'
		QDesktopServices.openUrl(QUrl(helpUrl))

	#def openHelp

	@Slot()
	def closeApplication(self):

		self.closeGui=False

		if self.changesInLoginSettings:
			self.showChangesDialog=True
		else:
			self.closeGui=True
			self.n4dMan.writeLog("Close Session")

	#def closeApplication
	
#class LliurexLoginControl

