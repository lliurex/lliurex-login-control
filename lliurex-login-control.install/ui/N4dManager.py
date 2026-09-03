#!/usr/bin/python3

from enum import IntEnum

import n4d.client
import os
import subprocess
import sys
import syslog
import json
import codecs
import pwd
import grp

class N4dManager:

	APPLY_CHANGES_SUCCESSFUL=10
	WARNING_CDC_ACTIVATION_REQUIRED=20
	CHANCE_LOGIN_ERROR=-10
	CHANGE_AUTOLOGIN_PASSWORD_ERROR=-20
	CHANGE_AUTOLOGIN_STATUS_ERROR=-30
	CHANGE_MULTIPLE_ERROR=-40
	ERROR_PASSWORDS_NOT_MATCH=-50
	ERROR_PASSWORD_EMPTY=-60
	ERROR_LOADING_CONFIGURATION=-70
	CHANGE_GUEST_USER_ERROR=-80

	KIRIGAMI_MSG_OK=0
	KIRIGAMI_MSG_ERROR=1
	KIRIGAMI_MSG_WARNING=2
	KIRIGAMI_MSG_INFO=3

	class WifiMode(IntEnum):
		
		DISABLE=0
		ENABLE=1
		LEGACY=2
		AUTOLOGIN=3
		EASYLOGIN=4
		EASYLOGINWIRED=5

	#class WifiMode

	def __init__(self):

		self.debug=True
		self.isWifiEnabled=False
		self.currentLoginOption=1
		self.currentPassword=""
		self.currentAutologinStatus=False
		self.isGuestUserEnabled=False
		
	#def __init__

	def setServer(self,ticket):
		
		ticket=ticket.replace('##U+0020##',' ')
		self.currentUser=ticket.split(' ')[2]
		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk)

		self.writeLog("Init session in lliurex-login-control GUI")
		self.writeLog(f"User login in GUI: {self.currentUser}")
	
	#def setServer

	def loadConfig(self,step="Initial"):

		try:
			self.writeLog(f"Login Control. {step} configuration:")
			loginOption=self.client.WifiEduGva.get_settings()
			wifiPassword=self.client.WifiEduGva.get_autologin()
			self.currentAutologinStatus=self._checkIfAutologinIsEnabled()
			self.isGuestUserEnabled=self._checkIfGuestUserIsEnabled()
		except Exception as e:
			self.writeLog(f"- Error loading configuration: {e}")
			return {"status":False,"code":N4dManager.ERROR_LOADING_CONFIGURATION,"type":N4dManager.KIRIGAMI_MSG_ERROR}

		if loginOption in N4dManager.WifiMode.__members__.values():
			if loginOption in (N4dManager.WifiMode.DISABLE,N4dManager.WifiMode.EASYLOGINWIRED):
				self.isWifiEnabled=False
			else:
				self.isWifiEnabled=True

			self.currentLoginOption=loginOption
			
		if wifiPassword is not None:
			self.currentPassword=wifiPassword

		self.currentLoginSettings={
			"isWifiEnabled":self.isWifiEnabled,
			"currentLoginOption":self.currentLoginOption,
			"currentPassword":wifiPassword if wifiPassword is not None else "",
			"isGuestUserEnabled":self.isGuestUserEnabled
		}

		self.writeLog(f"- Current Login Option: {self.currentLoginOption}")
		self.writeLog(f"- Autologin: {self.currentAutologinStatus}")
			
		return {"status":True,"code":"","type":""}

	#def loadConfig

	def applyChanges(self, info, confirmPasswordEntry):

		'''
		Actions in autologin:
			- -1: Nothing
			-  0: Enabled
			-  1: Disabled
			-  2: Updated Password
		'''

		changeLogin = False
		changePassword = False
		lastError = None
		actionAutologin = -1
		errorCount = 0

		currentPassword = info.get('currentPassword')
		confirmPassword = confirmPasswordEntry
		currentLoginOption=info.get("currentLoginOption")
		isGuestUserEnabled= info.get("isGuestUserEnabled")

		if currentLoginOption in (N4dManager.WifiMode.AUTOLOGIN,N4dManager.WifiMode.EASYLOGIN):
			if not currentPassword:
				return {"status": False, "code": N4dManager.ERROR_PASSWORD_EMPTY, "type": N4dManager.KIRIGAMI_MSG_ERROR}
			if (currentPassword != self.currentPassword) and (currentPassword != confirmPassword):
				return {"status": False, "code": N4dManager.ERROR_PASSWORDS_NOT_MATCH, "type": N4dManager.KIRIGAMI_MSG_ERROR}

		if currentLoginOption != self.currentLoginOption:
			changeLogin = True
			if currentLoginOption == N4dManager.WifiMode.AUTOLOGIN:
				actionAutologin = 0
			elif self.currentAutologinStatus:
				actionAutologin = 1

		if currentPassword != self.currentPassword:
			changePassword = True
			if currentLoginOption ==N4dManager.WifiMode.AUTOLOGIN and actionAutologin == -1:
				actionAutologin = 2 if self.currentAutologinStatus else 0
		
		if changeLogin:
			if currentLoginOption in (N4dManager.WifiMode.EASYLOGIN,N4dManager.WifiMode.EASYLOGINWIRED):
				ret=self._changeEasyLogin(True)
			else:
				if self.currentLoginOption in (N4dManager.WifiMode.EASYLOGIN,N4dManager.WifiMode.EASYLOGINWIRED):
				ret=self._changeEasyLogin(False)
								
			ret=self._changeLogin(currentLoginOption)
			lastError=ret.get("lastError",None)
			errorCount=errorCount+ret.get("errorCount",0)

		if changePassword:
			ret=self._changePassword(currentPassword)
			lastError=ret.get("lastError",None)
			errorCount=errorCount+ret.get("errorCount",0)

		if actionAutologin != -1:
			ret=self._changeAutoLogin(actionAutologin)
			lastError=ret.get("lastError",None)
			errorCount=errorCount+ret.get("errorCount",0)

		if isGuestUserEnabled != self.isGuestUserEnabled:
			ret=self._changeGuestUser(isGuestUserEnabled)
			lastError=ret.get("lastError",None)
			errorCount=errorCount+ret.get("errorCount",0)

		if errorCount > 1:
			return {"status": False, "code": N4dManager.CHANGE_MULTIPLE_ERROR, "type": N4dManager.KIRIGAMI_MSG_ERROR}
		if errorCount == 1:
			return {"status": False, "code": lastError, "type": N4dManager.KIRIGAMI_MSG_ERROR}

		self.loadConfig("End")

		return {"status": True, "code": N4dManager.APPLY_CHANGES_SUCCESSFUL, "type": N4dManager.KIRIGAMI_MSG_OK}

	#def applyChanges

	def _checkIfAutologinIsEnabled(self):

		try:
			return self.client.AlumnatAccountManager.get_alumnat_status().get('status',False)
		except Exception:
			return False

	#def _checkIfAutologinIsEnabled

	def _checkIfGuestUserIsEnabled(self):

		try:
			return self.client.GuestAccountManager.get_guest_status().get("status", False)
		except Exception:
			return False

	#def _checkIfGuestUserIsEnabled

	def _changeLogin(self,newLoginOption):

		result={
			"lastError":None,
			"errorCount":0 
		}

		self.writeLog("Changes in login configuration:")
		self.writeLog(f"- Action: Changed login Option to: {newLoginOption}")
		
		try:
			self.client.WifiEduGva.set_settings(newLoginOption)
			self.writeLog("- Result: Changes apply successful")
		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")
			result=~{
				"lastError":N4dManager.CHANCE_LOGIN_ERROR,
				"errorCount":1
			}

		return result

	#def _changeLogin

	def _changePassword(self, newPassword):

		result={
			"lastError":None,
			"errorCount":0 
		}
		
		self.writeLog("Changes in autologin password:")
		action_text = "Update password" if newPassword else "Clear password"
		self.writeLog(f"- Action: {action_text}")

		try:
			self.client.WifiEduGva.set_autologin(newPassword)
			self.writeLog("- Result: changes apply successful")
		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")
			result={
				"lastError":N4dManager.CHANGE_AUTOLOGIN_PASSWORD_ERROR,
				"errorCount":1
			}

		return result

	#def _changePassword

	def _changeAutoLogin(self, actionAutologin):

		result={
			"lastError":None,
			"errorCount":0 
		}

		self.writeLog("Changes in autologin")
		try:
			if actionAutologin == 0:
				self.writeLog("- Action: Enable autologin")
				self.client.AlumnatAccountManager.enable_alumnat_user()
			elif actionAutologin == 1:
				self.writeLog("- Action: Disable autologin")
				self.client.AlumnatAccountManager.disable_alumnat_user()
			elif actionAutologin == 2:
				self.writeLog("- Action: Updated password")
				self.client.AlumnatAccountManager.fix_alumnat_password()

			self.writeLog("- Result: Changes apply successful")
		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")
			result={
				"lastError":N4dManager.CHANGE_AUTOLOGIN_STATUS_ERROR,
				"errorCount":1
			}

		return result

	#def _changeAutoLogin

	def _changeGuestUser(self,isGuestUserEnabled):

		result={
			"lastError":None,
			"errorCount":0 
		}

		self.writeLog("Changes in guest-user:")
		self.writeLog(f"- Action: Activate guest-user: {isGuestUserEnabled}")

		try:
			if isGuestUserEnabled:
				ret=self.client.GuestAccountManager.enable_guest_user().get('status',False)
			else:
				ret=self.client.GuestAccountManager.disable_guest_user().get('status',False)

			if ret:
				self.writeLog("- Result: Changes apply successful")
			else:
				self.writeLog(f"- Result: Error applying changes: {ret.get('msg')}")
				result={
					"lastError":N4dManager.CHANGE_GUEST_USER_ERROR,
					"errorCount": 1
				}

		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")
			result={
				"lastError":N4dManager.CHANGE_GUEST_USER_ERROR,
				"errorCount": 1
				}

		return result
	
	#def _changeGuestUser
	
	def _changeEasyLogin(self,activate):
		
		print("TO DO")
		
	#def _changeEasyLogin	
	
	def writeLog(self,msg):
		
		syslog.openlog("LOGIN-CONTROL")
		syslog.syslog(msg)
		
	#def writeLog

	def getIntegrationCDCStatus(self):

		try:
			return subprocess.call(["cdccli", "-t"], stdout=subprocess.DEVNULL) == 0
		except Exception:
			return False

	#def getIntegrationCDCStatus

#class N4dManager
