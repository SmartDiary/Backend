from deta import Base,Deta
from dotenv import load_dotenv
import os,uuid
from datetime import date,datetime
load_dotenv()
deta_key = os.getenv("DETA_KEY")

base_man = Deta(deta_key)

#sd_db = Base("diary_users")
sd_db=base_man.Base("diary_users")

#sd_db.put(
#init_ob = {"token":"algo","secret":"thisisme","memories":[]}
#init_nm = "nickname256"
#init_memo = "hello darkness my old friend"

#init_token = "910a33f0-a436-4df0-8663-00b343b3ee0c"
#print("finisheed")

def authUser(nickname,secret):
	fetch_res = sd_db.fetch({"key":nickname,"secret":secret})
	return fetch_res

def authToken(token_str):
	tokman = getTokenUsr(token_str)
	if tokman.count>0:
		return True
	else:
		return False


def getTokenUsr(token):
	fetch_res = sd_db.fetch({"token":token})
	return fetch_res


def mkUser(nickname,secret):
	token = str(uuid.uuid4())

	try:
		sd_db.insert({"token":token,"secret":secret,"memories":[]},nickname)
		return token
	except Exception as e:
		print("user exits")
		usr_dta = authUser(nickname,secret)
		print(usr_dta.items)
		token = str(uuid.uuid4())

		try:
			if (usr_dta.count > 0):
				print("updating")
				sd_db.update({"token":token},nickname)
				print("update oken: ",token)
				return token
			else:
				print("failed")
				return None
		except Exception as e:
			print(e)
			return None

		return None

def addMemory(token,memory):
	tk_data = getTokenUsr(token)

	if(tk_data.count==1):
		print(tk_data.items)
		tk_key = (tk_data.items)[0]["key"]
		try:
			sd_db.update({"memories":sd_db.util.append(memory)},tk_key)
			print("update finished", tk_key)
			return True
		except Exception as e:
			print(e)
			return False
	return False

def getMemory(token):
	tk_data = getTokenUsr(token)

	if(tk_data.count==1):
		return (tk_data.items)[0]["memories"]
	else:
		return []


def updateMemory(token,memories):
	tk_data = getTokenUsr(token)

	if(tk_data.count==1):
		tk_key = (tk_data.items)[0]["key"]
		try:
			sd_db.update({"memories":memories},tk_key)
			print("update finished", tk_key)
			return True
		except Exception as e:
			print(e)
			return False
	return False

#tk = updateMemory(init_token,["fly away","for ever"])
#tk = getMemory(init_token)
#print(tk)

print(date.today())

print(datetime.now().strftime("%H:%M:%S"))