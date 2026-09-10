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
	WARNING_EASYLOGIN_ACTIVATION=30
	WARNING_AUTOLOGIN_ACTIVATION=40

	ERROR_LOADING_CONFIGURATION=-10
	CHANCE_LOGIN_ERROR=-20
	ERROR_ACTIVATING_AUTOLOGIN=-30
	ERROR_DEACTIVATING_AUTOLOGIN=-40
	ERROR_ACTIVATING_EASYLOGIN=-50
	ERROR_DEACTIVATING_EASYLOGIN=-60
	CHANGE_GUEST_USER_ERROR=-70
	CHANGE_MULTIPLE_ERROR=-80
	ERROR_PASSWORDS_NOT_MATCH=-90
	ERROR_PASSWORD_EMPTY=-100
	ERROR_CHANGING_PASSWORD=-110

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
		self.isAutoLoginEnabled=False
		self.isGuestUserEnabled=False
		self.isEasyLoginEnabled=False
		
	#def __init__

	def setServer(self,ticket):
		
		ticket=ticket.replace('##U+0020##',' ')
		self.currentUser=ticket.split(' ')[2]
		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk)

		self.writeLog("Init session in lliurex-login-control GUI")
		self.writeLog(f"User login in GUI: {self.currentUser}")
	
	#def setServer

	def loadConfig(self, step="Initial"):

		self.writeLog(f"Login Control. {step} configuration:")

		try:
			loginOption = self.client.WifiEduGva.get_settings()
			wifiPassword = self.client.WifiEduGva.get_autologin()
			self.isAutoLoginEnabled = self._getAutoLoginStatus()
			self.isGuestUserEnabled = self._getGuestUserStatus()
			self.isEasyLoginEnabled = self._getEasyLoginStatus()
		except Exception as e:
			self.writeLog(f"- Error loading configuration: {e}")
			return {"status": False, "code": N4dManager.ERROR_LOADING_CONFIGURATION, "type": N4dManager.KIRIGAMI_MSG_ERROR}

		if loginOption in N4dManager.WifiMode.__members__.values():
			self.isWifiEnabled = loginOption not in (N4dManager.WifiMode.DISABLE, N4dManager.WifiMode.EASYLOGINWIRED)
			self.currentLoginOption = loginOption
		else:
			self.isWifiEnabled = getattr(self, "isWifiEnabled", False)
			self.currentLoginOption = getattr(self, "currentLoginOption", None)

		if wifiPassword is not None:
			self.currentPassword = wifiPassword
		elif not hasattr(self, "currentPassword"):
			self.currentPassword = ""

		self.currentLoginSettings = {
			"isWifiEnabled": self.isWifiEnabled,
			"currentLoginOption": self.currentLoginOption,
			"currentPassword": self.currentPassword,
			"isGuestUserEnabled": self.isGuestUserEnabled
		}

		self.writeLog(f"- Current Login Option: {self.currentLoginOption}")
		self.writeLog(f"- Guest User account enabled: {self.isGuestUserEnabled}")

		if step == "Initial":
			if loginOption in (N4dManager.WifiMode.EASYLOGIN, N4dManager.WifiMode.EASYLOGINWIRED):
				if not self.isEasyLoginEnabled:
					ret = self._changeEasyLogin("enable")
					if not ret.get("status"):
						return {"status": True, "code": N4dManager.WARNING_EASYLOGIN_ACTIVATION, "type": N4dManager.KIRIGAMI_MSG_WARNING}
					self.isEasyLoginEnabled = self._getEasyLoginStatus()

			elif loginOption == N4dManager.WifiMode.AUTOLOGIN:
				if not self.isAutoLoginEnabled:
					ret = self._changeAutoLogin(0)
					if not ret.get("status"):
						return {"status": True, "code": N4dManager.WARNING_AUTOLOGIN_ACTIVATION, "type": N4dManager.KIRIGAMI_MSG_WARNING}
					self.isAutoLoginEnabled = self._getAutoLoginStatus()

		return {"status": True, "code": "", "type": ""}

	#def loadConfig

	def applyChanges(self, info, confirmPasswordEntry):

		currentPassword = info.get('currentPassword')
		currentLoginOption = info.get("currentLoginOption")
		isGuestUserEnabled = info.get("isGuestUserEnabled")

		if currentLoginOption in (N4dManager.WifiMode.AUTOLOGIN, N4dManager.WifiMode.EASYLOGIN):
			if not currentPassword:
				return {"status": False, "code": N4dManager.ERROR_PASSWORD_EMPTY, "type": N4dManager.KIRIGAMI_MSG_ERROR}
			if currentPassword != self.currentPassword:
				if currentPassword != confirmPasswordEntry:
					return {"status": False, "code": N4dManager.ERROR_PASSWORDS_NOT_MATCH, "type": N4dManager.KIRIGAMI_MSG_ERROR}

		loginActions = []
		otherActions = []

		if currentLoginOption != self.currentLoginOption:
			if currentLoginOption == N4dManager.WifiMode.AUTOLOGIN:
				loginActions.append(lambda: self._changeAutoLogin(0))
			elif currentLoginOption in (N4dManager.WifiMode.EASYLOGIN, N4dManager.WifiMode.EASYLOGINWIRED):
				loginActions.append(lambda: self._changeEasyLogin("enable"))

			loginActions.append(lambda: self._changeLogin(currentLoginOption))

			if currentLoginOption == N4dManager.WifiMode.AUTOLOGIN and self.isEasyLoginEnabled:
				loginActions.append(lambda: self._changeEasyLogin("disable"))
			elif currentLoginOption in (N4dManager.WifiMode.EASYLOGIN, N4dManager.WifiMode.EASYLOGINWIRED) and self.isAutoLoginEnabled:
				loginActions.append(lambda: self._changeAutoLogin(1))
			elif currentLoginOption not in (N4dManager.WifiMode.AUTOLOGIN, N4dManager.WifiMode.EASYLOGIN, N4dManager.WifiMode.EASYLOGINWIRED):
				if self.isAutoLoginEnabled: loginActions.append(lambda: self._changeAutoLogin(1))
				if self.isEasyLoginEnabled: loginActions.append(lambda: self._changeEasyLogin("disable"))

		if currentPassword != self.currentPassword:
			otherActions.append(lambda: self._changePassword(currentPassword))

		if isGuestUserEnabled != self.isGuestUserEnabled:
			otherActions.append(lambda: self._changeGuestUser(isGuestUserEnabled))

		errorCount = 0
		lastError = None

		self.writeLog("Changes in login configuration:")
		
		for action in loginActions:
			ret = action()
			if not ret.get("status"):
				errorCount += 1
				lastError = ret.get("lastError")
				break

		for action in otherActions:
			ret=action()
			if not ret.get("status"):
				errorCount += 1
				lastError = ret.get("lastError")

		if errorCount > 1:
			return {"status": False, "code": N4dManager.CHANGE_MULTIPLE_ERROR, "type": N4dManager.KIRIGAMI_MSG_ERROR}
		if errorCount == 1:
			if lastError not in (N4dManager.ERROR_DEACTIVATING_AUTOLOGIN,N4dManager.ERROR_DEACTIVATING_EASYLOGIN):
				return {"status": False, "code": lastError, "type": N4dManager.KIRIGAMI_MSG_ERROR}

		self.loadConfig("End")
		
		if lastError in (N4dManager.ERROR_DEACTIVATING_AUTOLOGIN,N4dManager.ERROR_DEACTIVATING_EASYLOGIN):
			return {"status": True, "code": lastError, "type": N4dManager.KIRIGAMI_MSG_WARNING}

		return {"status": True, "code": N4dManager.APPLY_CHANGES_SUCCESSFUL, "type": N4dManager.KIRIGAMI_MSG_OK}


	#def applyChanges

	def _getAutoLoginStatus(self):

		try:
			return self.client.AlumnatAccountManager.get_alumnat_status().get('status',False)
		except Exception:
			return False

	#def _getAutoLoginStatus

	def _getGuestUserStatus(self):

		try:
			return self.client.GuestAccountManager.get_guest_status().get("status", False)
		except Exception:
			return False

	#def _getGuestUserStatus

	def _changeLogin(self,newLoginOption):

		self.writeLog(f"- Action: Changed login option to: {newLoginOption}")

		try:
			self.client.WifiEduGva.set_settings(newLoginOption)
			self.writeLog("- Result: Changes apply successful")
			return {
				"status":True,
				"lastError":None
			}
		except Exception as e:
			print(f"ERROR: {e}")
			self.writeLog(f"- Result: Error applying changes: {e}")
			return {
				"status":False,
				"lastError":N4dManager.CHANCE_LOGIN_ERROR,
			}

	#def _changeLogin

	def _changePassword(self, newPassword):

		action_text = "Update password" if newPassword else "Clear password"
		self.writeLog(f"- Action: update alumnat password: {action_text}")

		try:
			self.client.WifiEduGva.set_autologin(newPassword)
			self.writeLog("- Result: changes apply successful")
			return {
				"status":True,
				"lastError":None
			}
		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")
			return {
				"status":False,
				"lastError":N4dManager.CHANGE_AUTOLOGIN_PASSWORD_ERROR
			}

	#def _changePassword

	def _changeAutoLogin(self, actionAutoLogin):

		try:
			if actionAutoLogin == 0:
				self.writeLog("- Action: Enable autologin")
				lastError=N4dManager.ERROR_ACTIVATING_AUTOLOGIN
				ret=self.client.AlumnatAccountManager.enable_alumnat_user()
			elif actionAutoLogin == 1:
				self.writeLog("- Action: Disable autologin")
				lastError=N4dManager.ERROR_DEACTIVATING_AUTOLOGIN
				ret=self.client.AlumnatAccountManager.disable_alumnat_user()

			if ret.get("status",False):
				self.writeLog("- Result: Changes apply successful")
				return {
					"status":True,
					"lastError":None
				}
			else:
				self.writeLog(f"- Result: Error applying changes: {ret.get('msg')}")

		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")

		return {
			"status":False,
			"lastError": lastError
		}

	#def _changeAutoLogin

	def _changeGuestUser(self,isGuestUserEnabled):

		self.writeLog(f"- Action: Activate guest-user: {isGuestUserEnabled}")

		try:
			if isGuestUserEnabled:
				ret=self.client.GuestAccountManager.enable_guest_user()
			else:
				ret=self.client.GuestAccountManager.disable_guest_user()

			if ret.get('status',False):
				self.writeLog("- Result: Changes apply successful")
				return {
					"status":True,
					"lastError":None,
				}

			else:
				self.writeLog(f"- Result: Error applying changes: {ret.get('msg')}")
	
		except Exception as e:
			self.writeLog(f"- Result: Error applying changes: {e}")

		return {
			"status":False,
			"lastError":N4dManager.CHANGE_GUEST_USER_ERROR
		}
	
	#def _changeGuestUser

	def _getEasyLoginStatus(self):

		cmd=["easyclientctl","status"]

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				return True
		
		except FileNotFoundError:
			self.writeLog(f"- StatusEasyLogin: get status error: Exec not found in the system")

		return False

	#def _getEasyLoginStatus
	
	def _changeEasyLogin(self,action):

		self.writeLog(f"- Action: {action} easylogin")
		
		cmd=["sudo","easyclientctl",action]

		if action=="enable":
			lastError=N4dManager.ERROR_ACTIVATING_EASYLOGIN
		else:
			lastError=N4dManager.ERROR_DEACTIVATING_EASYLOGIN

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				self.writeLog("- Result: Changes apply successful")
				return {
					"status":True,
					"lastError":None,
				}
			else:
				self.writeLog(" - Result: Error applying changes")
	
		except FileNotFoundError:
			self.writeLog(f"- Result: Error applying changes: Exec not found in the system")

		return {
			"status":False,
			"lastError":lastError
		}

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
