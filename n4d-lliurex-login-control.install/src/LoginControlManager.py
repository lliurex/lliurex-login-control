import os
import subprocess
import n4d.responses

class LoginControlManager:
	
	def __init__(self):
	
		pass	
	
	#def init
	
	def startup(self,options):
		
		pass
	
	#def startup	
	
	def get_easylogin_client_status(self):
		
		cmd=["sudo","easyclientctl","status"]
		
		result={
			"status":False,
			"msg":None
		}

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				result["status"]=True
		
		except FileNotFoundError:
			result["msg"]="EasyLogin-Client: Error getting status: Exec not found in the system"

		except Exception as e:
			result["msg"]=f"EasyLogin-Client: Unexpect error: {e}"

		print(f"RESULT: {result}")
		return n4d.responses.build_successful_call_response(result)
		
	#def get_easylogin_client_status

	def enable_easylogin_client(self):

		cmd=["sudo","easyclientctl","enable"]
		
		result={
			"status":False,
			"msg":None
		}

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				result["status"]=True
		
		except FileNotFoundError:
			result["msg"]="EasyLogin-Client: Error enabling: Exec not found in the system"

		except Exception as e:
			result["msg"]=f"EasyLogin-Client: Unexpect error: {e}"
		
		print(f"RESULT: {result}")
		return n4d.responses.build_successful_call_response(result)

	#def enable_easylogin_client

	def disable_easylogin_client(self):

		cmd=["sudo","easyclientctl","disable"]
		
		result={
			"status":False,
			"msg":None
		}

		try:
			ret=subprocess.run(cmd,capture_output=True,text=True)
			if ret.returncode==0:
				result["status"]=True
		
		except FileNotFoundError:
			result["msg"]="EasyLogin-Client: Error disabling: Exec not found in the system"

		except Exception as e:
			result["msg"]=f"EasyLogin-Client: Unexpect error: {e}"

		print(f"RESULT: {result}")
		return n4d.responses.build_successful_call_response(result)

	#def disable_easylogin_client
				
		
#class LoginControlManager


if __name__=="__main__":
	
	lcm=LoginControlManager()
	
