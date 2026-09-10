#!/usr/bin/env python3

from enum import IntEnum

import os
import subprocess
import n4d.client
import sys
import syslog
import pwd
import grp
import getpass
import signal
import codecs

signal.signal(signal.SIGINT,signal.SIG_IGN)

class LoginControlCliManager(object):

	class WifiMode(IntEnum):
		
		DISABLE=0
		ENABLE=1
		LEGACY=2
		AUTOLOGIN=3
		EASYLOGIN=4
		EASYLOGINWIRED=5

	#class WifiMode

	def __init__(self,mode):
		
		self.isWifiConnectionEnabled=False
		self.currentLoginOption=-1
		self.isAlumnatPasswordConfigured=False
		self.currentAlumnatPassword=None
		self.isCDCIntegrationEnabled=False
		self.isGuestUserEnabled=False
		self.isAutologinConfigured=False
		self.isEasyLoginConfigured=False
		self.currentUser=""
		self.unattendedMode=mode
		self.easyLoginActivationFailed=False
		self.autoLoginActivationFailed=False
		self.n4dClient=n4d.client.Client()
		self._getCurrentUser()
		self._getInfo("Initial")

	#def __init__

	def showCurrentConfig(self):

		self._writeLog("- Action: get current configuration")
		self._createClient()

		print('   [Login-Control]: Current configuration')
		print(f'      - Wifi Connection Enabled: {self.isWifiConnectionEnabled}')
		if self.isWifiConnectionEnabled:
			defaultOption=self._mappingWifiOptionEnabled(self.currentLoginOption,"IntToText")
		else:
			defaultOption=self._mappingWifiOptionDisabled(self.currentLoginOption,"IntToText")

		print(f'      - Default login Option: {defaultOption}')
		print(f'      - Password for alumnat user configured: {self.isAlumnatPasswordConfigured}')

		print(f'      - Guest user account enabled: {self.isGuestUserEnabled}')

		if self.easyLoginActivationFailed:
			print('   [Login-Control]: WARNING The default login option is configured to use EASYLOGIN but its activation has failed')

		if self.autoLoginActivationFailed:
			print('   [Login-Control]: WARNING The default login option is configured to use AUTOLOGIN but its activation has failed')

		if self.isWifiConnectionEnabled and self.currentLoginOption not in (LoginControlCliManager.WifiMode.AUTOLOGIN,LoginControlCliManager.WifiMode.EASYLOGIN):
			if not self.isCDCIntegrationEnabled:
				print('   [Login-Control]: WARNING It is necessary to activate the integration with ID to be able to log in with WIFI GVA')

		return 0
	
	#def showCurrentConfig

	def showAlumnatPassword(self):

		self._writeLog("- Action: get current password for alumnat user")
		self._createClient()

		if self.currentAlumnatPassword is not None:
			print(f'   [Login-Control]: Current password for alumnat user: {self.currentAlumnatPassword}')
		else:
			print('   [Login-Control]: Password for alumnat user not configured')
	
		return 0

	#def showAlumnatPassword

	def enableWifi(self,loginOption,password=None,confirmPassword=None):

		loginValue=self._mappingWifiOptionEnabled(loginOption,"TextToInt")
		forcePasswordUpdate=False

		if loginValue==-1:
			print('   [Login-Control]: The option indicated for login is not valid')
			return 0

		if loginValue==self.currentLoginOption:
			print('   [Login-Control]: Wifi connection with the indicated login option already configured. Nothing to do')
			return 0

		simpleLoginOptions=loginValue in (LoginControlCliManager.WifiMode.AUTOLOGIN,LoginControlCliManager.WifiMode.EASYLOGIN)
		
		if simpleLoginOptions: 
			if not self.isAlumnatPasswordConfigured:
				if not self._checkPassword(password,confirmPassword):
					return 0
			else:
				if password and password!=self.currentAlumnatPassword:
					if not self._checkPassword(password,confirmPassword):
						return 0
					forcePasswordUpdate=True
		
		if not self.unattendedMode:
			response=input('   [Login-Control]: Do you want to enable Wifi connection and change the default login option? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Login-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in the login settings")
			
			ret=True
			self._createClient()

			if loginValue==LoginControlCliManager.WifiMode.EASYLOGIN and not self.isEasyLoginConfigured:
				ret=self._changeEasyLogin("enable")
				if not ret:
					print(f'   [Login-Control]: Error. Unable to enable Easy-Login')
					return 1
			elif loginValue==LoginControlCliManager.WifiMode.AUTOLOGIN and not self.isAutologinConfigured:
				ret=self._changeAutologin("enable")
				if not ret:
					print(f'   [Login-Control]: Error. Unable to enable Auto-Login')
					return 1

			if simpleLoginOptions:
				if not self.isAlumnatPasswordConfigured or forcePasswordUpdate:
					self._writeLog("- Action: set password for alumnat user")
					ret=self.n4dClient.WifiEduGva.set_autologin(password)
					self._writeLog("- Result: Changes apply successful")

			self._writeLog(f"- Action: Changed login option to: {loginValue}")
			ret=self.n4dClient.WifiEduGva.set_settings(int(loginValue))
			self._writeLog("- Result: Changes apply successful")
			print('   [Login-Control]: Action completed successfull')

			if loginValue != LoginControlCliManager.WifiMode.AUTOLOGIN and self.isAutologinConfigured:
				ret=self._changeAutologin("disable")
				if not ret:
					print(f'   [Login-Control]: Warning. Unable to disable AUTOLOGIN setting')
			
			if loginValue != LoginControlCliManager.WifiMode.EASYLOGIN and self.isEasyLoginConfigured:
				ret=self._changeEasyLogin("disable")
				if not ret:
					print(f'   [Login-Control]: Warning. Unable to disable EASYLOGIN setting')

			self._getInfo("End")
			
			if not simpleLoginOptions and not self.isCDCIntegrationEnabled:
				print('   [Login-Control]: WARNING It is necessary to activate the integration with ID to be able to log in with WIFI GVA')
			
			return 0

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print(f'   [Login-Control]: Error. Unable to change login settings')
			return 1
					
	#def enableWifi

	def disableWifi(self,loginOption):

		loginValue=self._mappingWifiOptionDisabled(loginOption,"TextToInt")

		if loginValue==-1:
			print('   [Login-Control]: The option indicated for login is not valid')
			return 0

		if loginValue==self.currentLoginOption:
			print('   [Login-Control]:  Wifi connection with the indicated login option already configured. Nothing to do')
			return 0
	
		if not self.unattendedMode:
			response=input('   [Login-Control]: Do you want to disable Wifi connection and change the default login option? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Login-Control]: Action canceled')
			return 0
		
		try:
			self._writeLog("Changes in the login settings:")
			
			self._createClient()

			simpleLoginOptions=loginOption == LoginControlCliManager.WifiMode.EASYLOGINWIRED
			
			if simpleLoginOptions and not self.isEasyLoginConfigured:
				ret=self._changeEasyLogin("enable")
				if not ret:
					print(f'   [Login-Control]: Error. Unable to enable Easy-Login')
					return 1
		
			self._writeLog(f"- Action: Changed login option to: {loginValue}")
			ret=self.n4dClient.WifiEduGva.set_settings(int(loginValue))
			self._writeLog("- Result: Changes apply successful")
			print('   [Login-Control]: Action completed successfull')

			if self.isAutologinConfigured:
				ret=self._changeAutologin("disable")
				if not ret:
					print(f'   [Login-Control]: Warning. Unable to disable AUTOLOGIN setting')

			if not simpleLoginOptions and self.isEasyLoginConfigured:
				ret=self._changeEasyLogin("disable")
				if not ret:
					print(f'   [Login-Control]: Warning. Unable to disable AUTOLOGIN setting')
			
			self._getInfo("End")
			return 0

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Login-Control]: Error. Unable to change login settings')
			return 1

	#def disableWifi

	def updateAlumnatPassword(self,password,confirmPassword):

		if not self._checkPassword(password,confirmPassword):
			return 0
		
		if password==self.currentAlumnatPassword:
			print('   [Login-Control]: Password of alumnat user already exists. Nothing to do')
			return 0

		if not self.unattendedMode:
			response=input('   [Login-Control]: Do you want to update the password of the alumnat user? (yes/no)): ').lower()
		else:
			response='yes'
			
		if not response.startswith('y'):
			print('   [Login-Control]: Action canceled')
			return 0
		
		try:
			self._writeLog("Changes in the login settings:")
			self._writeLog('- Action: update alumnat password')
			self._createClient()
			ret=self.n4dClient.WifiEduGva.set_autologin(password)
			self._writeLog("- Result: changes apply successful")
			print('   [Login-Control]: Action completed successfull')
			return 0

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Login-Control]: Error. Unable to update password of alumnat user')
			return 1
	
	#def updateAlumnatPassword

	def removeAlumnatPassword(self):

		if not self.isAlumnatPasswordConfigured:
			print('   [Login-Control]: Password for alumnat user already removed. Nothing to do')
			return 0

		if self.currentLoginOption in (LoginControlCliManager.WifiMode.AUTOLOGIN,LoginControlCliManager.WifiMode.EASYLOGIN):
			print('   [Login-Control]: Password for alumnat user cannot be deleted because the AUTOLOGIN or EASYLOGIN option is activated')
			return 0
		
		if not self.unattendedMode:
			response=input('   [Login-Control]: Do you want to remove the password of alumnat user? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Login-Control]: Action canceled')
			return 0
			
		try:
			self._writeLog("Changes in the login settings:")
			self._writeLog('- Action: remove alumnat password')
			self._createClient()
			ret=self.n4dClient.WifiEduGva.set_autologin("")
			self._writeLog("- Result: changes apply successful")
			print('   [Login-Control]: Action completed successfull')
			self._getInfo("End")
			return 0

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}"%e.code)
			print('   [Login-Control]: Error. Unable to remove password of alumnat user')
			return 1

	#de removeAlumnatPassword

	def enableGuestUser(self):

		if not self.unattendedMode:
			response=input('   [Login-Control]: Do you want to enable a guest user account? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Login-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in the login settings:")
			self._writeLog(f"- Action: enable guest-user account")
			self._createClient()
			ret=self.n4dClient.GuestAccountManager.enable_guest_user()

			if ret.get('status',False):
				self._writeLog("- Result: Changes apply successful")
				print('   [Login-Control]: Action completed successfull')
				self._getInfo("End")
				return 0
			else:
				self._writeLog(f"- Result: Error applying changes: {ret.get('msg')}")
				print('   [Login-Control]: Error. Unable to enable guest-user account')
				return 1

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Login-Control]: Error. Unable to enable guest-user account')
			return 1

	#def enableGuestUser

	def disableGuestUser(self):

		if not self.unattendedMode:
			response=input('   [Login-Control]: Do you want to disable a guest user account? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Login-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in the login settings:")
			self._writeLog(f"- Action: disable guest-user account")
			self._createClient()
			ret=self.n4dClient.GuestAccountManager.disable_guest_user()

			if ret.get('status',False):
				self._writeLog("- Result: Changes apply successful")
				print('   [Login-Control]: Action completed successfull')
				self._getInfo("End")
				return 0
			else:
				self._writeLog(f"- Result: Error applying changes: {ret.get('msg')}")
				print('   [Login-Control]: Error. Unable to disable guest-user account')
				return 1

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Login-Control]: Error. Unable to disable guest-user account')
			return 1

	#def disableGuestUser

	def n4dUpdatePassword(self,password):

		if self.currentUser!="":
			print('   [Login-Control]: Option valid only for schedled password changes')
			return 0
		if not self.isAlumnatPasswordConfigured:
			return 0
		
		try:
			self._writeLog("Changes in the login settings:")
			self._writeLog('- Action: update alumnat password (with n4d one-shot)')
			self._createClient()
			tmpPassword=codecs.decode(password,'rot13')
			ret=self.n4dClient.WifiEduGva.set_autologin(tmpPassword)
			self._writeLog("- Result: changes apply successful")
			print('   [Login-Control]: Action completed successfull')
			self._getInfo("End")
			return 0

		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Login-Control]: Error. Unable to update password of alumnat user')
			return 1

	#def n4dUpdatePassword

	def _createClient(self):

		if self.currentUser!="":
			password=getpass.getpass('   [Login-Control]: Enter your password:')
			client=n4d.client.Client("https://localhost:9779",self.currentUser,password)
			
			try:
				ticket=client.get_ticket()
				self.n4dClient=n4d.client.Client(ticket=ticket)
			except Exception as e:
				msg="Authentication failed. Unable to execute action"
				self._writeLog(msg)
				print(f"   [Login-Control]: {msg}")
				sys.exit(1)
		else:
			masterKey=n4d.client.Key.master_key()
			
			if masterKey.valid():
				self.n4dClient=n4d.client.Client(key=masterKey)
			else:
				print('   [Login-Control]: You need root privilege to run this tool')

	#def _createClient

	def _getInfo(self,step="Initial"):

		self.easyLoginActivationFailed=False
		self.autoLoginActivationFailed=False

		try:
			self._writeLog(f"Login Control. {step} configuration")
			wifiConfiguration=self.n4dClient.WifiEduGva.get_settings()
			wifiPassword=self.n4dClient.WifiEduGva.get_autologin()
			self.isAutologinConfigured=self._getAutoLoginStatus()
			self.isGuestUserEnabled=self._getGuestUserStatus()
			self.isEasyLoginConfigured=self._getEasyLoginStatus()

			if wifiConfiguration in LoginControlCliManager.WifiMode.__members__.values():
				if wifiConfiguration in (LoginControlCliManager.WifiMode.DISABLE,LoginControlCliManager.WifiMode.EASYLOGINWIRED):
					self.isWifiConnectionEnabled=False
					self.currentLoginOption=wifiConfiguration
				else:
					self.isWifiConnectionEnabled=True
					self.currentLoginOption=wifiConfiguration

			if not wifiPassword:
				self.isAlumnatPasswordConfigured=False
			else:
				self.isAlumnatPasswordConfigured=True
				self.currentAlumnatPassword=wifiPassword

			self.isCDCIntegrationEnabled=self._getIntegrationCDCStatus()

			self._writeLog(f"- Current Login Option: {wifiConfiguration}")
			self._writeLog(f"- Password for alumnat user configured: {self.isAlumnatPasswordConfigured}")
			self._writeLog(f"- Guest User account enabled: {self.isGuestUserEnabled}")
			
			if step=="Initial":
				if self.currentLoginOption in (LoginControlCliManager.WifiMode.EASYLOGIN,LoginControlCliManager.WifiMode.EASYLOGINWIRED):
					if not self.isEasyLoginConfigured:
						if not self._changeEasyLogin("enable"):
							self.easyLoginActivationFailed=True
						self.isEasyLoginConfigured=self._getEasyLoginStatus()
				elif self.currentLoginOption == LoginControlCliManager.WifiMode.AUTOLOGIN:
					if not self.isAutologinConfigured:
						if not self.n4dClient.AlumnatAccountManager.enable_alumnat_user().get("status"):
							self.autoLoginActivationFailed=True
						self.isAutologinConfigured=self._getAutoLoginStatus()
			return True

		except Exception as e:
			self._writeLog(f"- Error loading configuration: {e}")
			return False

	#def _getInfo

	def _mappingWifiOptionEnabled(self,wifiOption,mappingType):

		if mappingType=="TextToInt":
			mapping ={
				"CREDENTIALS":LoginControlCliManager.WifiMode.ENABLE,
				"AUTOLOGIN": LoginControlCliManager.WifiMode.AUTOLOGIN,
				"EASYLOGIN": LoginControlCliManager.WifiMode.EASYLOGIN,
			}
			return mapping.get(wifiOption,-1)
		else:
			mapping={
				LoginControlCliManager.WifiMode.ENABLE:"CREDENTIALS",
				LoginControlCliManager.WifiMode.LEGACY:"CREDENTIALS",
				LoginControlCliManager.WifiMode.AUTOLOGIN:"AUTOLOGIN",
				LoginControlCliManager.WifiMode.EASYLOGIN:"EASYLOGIN"
			}
			return mapping.get(wifiOption,"UNKNOWN")

	#def _mappingWifiOptionEnabled

	def _mappingWifiOptionDisabled(self,wifiOption,mappingType):

		if mappingType=="TextToInt":
			mapping ={
				"CREDENTIALS":LoginControlCliManager.WifiMode.DISABLE,
				"EASYLOGIN": LoginControlCliManager.WifiMode.EASYLOGINWIRED,
			}
			return mapping.get(wifiOption,-1)
		else:
			mapping={
				LoginControlCliManager.WifiMode.DISABLE:"CREDENTIALS",
				LoginControlCliManager.WifiMode.EASYLOGINWIRED:"EASYLOGIN"
			}
			return mapping.get(wifiOption,"UNKNOWN")

	#def _mappingWifiOptionDisabled

	def _getAutoLoginStatus(self):

		try:
			ret=self.n4dClient.AlumnatAccountManager.get_alumnat_status().get('status',False)
		except:
			ret=False

		return ret

	#def _getAutoLoginStatus

	def _getGuestUserStatus(self):

		try:
			ret=self.n4dClient.GuestAccountManager.get_guest_status().get("status", False)
		except Exception as e:
			ret=False

		return ret

	#def _getGuestUserStatus

	def _checkPassword(self,password,confirmPassword):

		if not password:
			print('   [Login-Control]: No password has been indicated for the alumnat user')
			return False
		
		if password!=confirmPassword:
			print('   [Login-Control]: The given passwords for the alumnat user do not match')
			return False

		return True

	#def _checkPassword

	def _getEasyLoginStatus(self):

		cmd=["easyclientctl","status"]

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				return True
		
		except subprocess.CalledProcessError as e:
			self._writeLog(f"- StatusEasyLogin: get status error: {e.returncode}")

		except FileNotFoundError:
			self._writeLog(f"- StatusEasyLogin: get status error: Exec not found in the system")

		return False

	#def _getEasyLoginStatus

	def _changeEasyLogin(self,action):

		self._writeLog(f"- Action: {action} EASYLOGIN")

		cmd=["sudo","easyclientctl",action]

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				self._writeLog("- Result: Changes apply successful")
				return True
			else:
				self._writeLog("- Result: Error applying changes")
	
		except FileNotFoundError:
			self._writeLog(f"- Result: Error applying changes: Exec not found in the system")

		return False
					
	#def _changeEasyLogin

	def _changeAutologin(self,action):

		self._writeLog(f"- Action: {action} AUTOLOGIN")

		try:
			if action == "enable":
				ret=self.n4dClient.AlumnatAccountManager.enable_alumnat_user()
			else:
				ret=self.n4dClient.AlumnatAccountManager.disable_alumnat_user()

			if ret.get("status",False):
				self._writeLog("- Result: Changes apply successful")
				return True
			else:
				self._writeLog(f"- Result: Error applying changes: {ret.get('msg')}")

		except Exception as e:
			self._writeLog(f"- Result: Error applying changes: {e}")

		return False

	#def _changeAutoLogin

	def _getCurrentUser(self):

		sudoUser=os.environ.get("SUDO_USER","")
		loginUser=""
		pkexecUser=""

		try:
			loginUser=os.getlogin()
		except:
			pass

		pkexec_uid=os.environ.get("PKEXEC_UID")
		if pkexec_uid:
			try:
				pkexecUser=subprocess.check_output(["id", "-un", pkexec_uid]).decode().strip()
			except:
				pass

		if pkexecUser and pkexecUser !="root":
			self.currentUser=pkexecUser

		elif sudoUser and sudoUser!="root":
			self.currentUser=sudoUser
			
		else:
			self.currentUser=loginUser

		self._writeLog("Init session in lliurex-Login-Control CLI")
		if loginUser:
			self._writeLog(f"User login in CLI: {self.currentUser}")
		else:
			self._writeLog("User login in CLI: No current user detected. A script may have been executed at login")

		if self.unattendedMode:
			self.currentUser=""
			
		self._writeLog(f"Unattended Mode:{self.unattendedMode}")

	#def _getCurrentUser

	def _getIntegrationCDCStatus(self):

		try:
			result=subprocess.run(["cdccli","-t"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			return result.returncode==0
		except FileNotFoundError:
			return False

	#def _getIntegrationCDCStatus

	def _writeLog(self,msg):

		syslog.openlog("LOGIN-CONTROL")
		syslog.syslog(msg)

	#def _writeLog

#class LoginControlCliManager	



