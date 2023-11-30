from detadb import *
from datetime import date,datetime
import openai
from bs4 import BeautifulSoup
import langman,time
#from dotenv import load_dotenv

#load_dotenv()

big_len = 36


openai.api_key = os.environ["OPENAI_API_KEY"]
print("using openai ",openai.api_key)
def gen_db_id(name):
    name_len = len(name)
    rem_len = (big_len - name_len)
    namex=name+key_stat[:rem_len]
    return namex

def awaddmem(cookie,mem_data):

    title = mem_data["title"]
    content = mem_data["content"]
    tags = mem_data["tags"]
    adate = date.today()
    time = datetime.now().strftime("%H:%M:%S")

    memory = f"use_title:'{title}' use_content:'{content}' use_tags:'{tags}' use_date:'{adate}' use_time:'{time}'"
    memory_stat = addMemory(cookie,memory)

    if(memory_stat==True):
    	return {"ok":True,"content":"memory noted"}
    else:
    	return {"ok":False,"content":"memory error"}

def rawaddmem(cookie,mem_data):

    title = mem_data["title"]
    content = mem_data["content"]
    tags = mem_data["tags"]
    adate = date.today()
    time = datetime.now().strftime("%H:%M:%S")

    memory = f"use_title:'{title}' use_content:'{content}' use_tags:'{tags}' use_date:'{adate}' use_time:'{time}'"
    memory_stat = addMemory(cookie,memory)

    if(memory_stat==True):
    	return {"ok":True,"content":"memory noted"}
    else:
    	return {"ok":False,"content":"memory error"}



def awgetmems(cookie,mem_data):
    #name = cookie
    #if (len(name)<=0):
		#     return None
    memories = getMemory(cookie)

    return memories


def xgptEat(cookie,json_std):
    mems = awgetmems(cookie,json_std)
    my_gpt_msg = [
    {
      "role": "system",
      "content": "hello, please act as a caring friend who has the capability of saving, recalling, understanding and digesting the memories i will be providing. Each memory will have a memory id which i will tell you via the key word use_mem_id: 'memory_id' , each memory will also have a memory title which i will tell you using the key word use use_mem_header: 'memory_title' , each memory will also contain the content which will be identified by the keyword use_mem_data: 'memory contents' , each memory will also contain tags represented by use_mem_tags: 'memory tags' . Each memory will have a date tag identified by use_date:'year-month-date' and a time tag identified by use_time in the format hours : minutes: seconds, the use_date and use_time identifies show when the memory was recorded. i will later ask you questions about the different memories that i will provide so that you help me recall them and answer any questions about the memories. Each question will have a tag ref_date:'year-month-date' and tag ref_time:'hours:minutes:seconds' to show when it was asked. Incase i ask about date or time, use the use the ref_date, ref_time, use_date, use_time values for any date and time related calculations. you don't need to show me the workings. thanks, in the answers, don't show the tags identifiers. thanks"
    }]


    for mem in mems:
        my_gpt = {"role": "user","content": ""}
        my_gpt['content']=mem
        my_gpt_msg.append(my_gpt)
    qtn = json_std["query"]
    xmy_gpt = {
      "role": "user",
      "content": ""
    }
    xmy_gpt["content"] = "from my memories answer this: "+str(qtn)
    my_gpt_msg.append(xmy_gpt)
    print(my_gpt_msg)
    return my_gpt_msg

def gptEat(cookie,json_std):
    mems = awgetmems(cookie,json_std)
    
    qtn = json_std["query"]
  
    adate = date.today()
    time = datetime.now().strftime("%H:%M:%S")

    memory = f"{qtn} ref_date:'{adate}' ref_time:'{time}'"
    my_gpt_msg = langman.total_recall(mems,memory)
    #print(my_gpt_msg)
    return my_gpt_msg


def awcreatedb(json_std):
    name = json_std["nickname"]
    secret = json_std["secret"]

    token = mkUser(name,secret)
    return token
#int(os.environ.get("OPENAI_MAX_TOKENS", "512"))
def xhandlePrompt(token,prompt):
		print(prompt)
	#try:
		response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		max_tokens=256,
		messages=prompt,
		temperature =1
		)
		completion = response.choices[0].message.content
		prompt.append(completion)
		print(completion)

		prompt_json = {"role":"assistant","content":completion}
		#updateMemory(token,prompt)
		json_data= {"ok": True, "content": completion}
		return json_data
	#except Exception as ex:
	#	print(ex)
		json_error = {"ok": False, "content": "Failed to query model."}
		return json_error

def handlePrompt(token,prompt):
  return langman.askMem(prompt)


def parseMem(memory_ans):
  soup = BeautifulSoup(memory_ans,"xml")
  mem_error = soup.find("mem_error_502")
  return mem_error.text

def execPrompt(mtoken,prompt):
  my_prompts = gptEat(mtoken,prompt)
  
  prompts_dta = []
  ctx = 0
  for my_prompt in my_prompts:
    print("\neating my prompt: ",my_prompt)
    if ctx>0:
      time.sleep(21)
    prompt_dta = handlePrompt(mtoken,my_prompt)
    prompts_dta.append(prompt_dta)
    ctx = ctx+1
  return prompts_dta

def urlEater(mtoken,mem_data):
    url_link = mem_data["content"]
    #url_parts = url_link.split('/')
    #url_title = url_link[len(url_parts)-1]
    
    url_sum = langman.eatUrl(url_link)
    
    if len(url_sum) > 0:
      #xmem_data["title"] = url_title
      #xmem_data["content"] = url_sum
      #xmem_data["tags"] = ''
      awaddmem(mtoken,url_sum)
      return True
    else:
      return False