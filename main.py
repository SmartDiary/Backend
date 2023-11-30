from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from bs4 import BeautifulSoup
from workman import *

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")

origins = ["http://localhost","http://192.168.1.152:3000","http://localhost:3000","http://localhost:8008","http://192.168.1.151","http://192.168.1.151:8008"]
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
	)

templates = Jinja2Templates(directory="static")

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
	return templates.TemplateResponse("index.html",context={"request":request})

@app.post("/")
async def process(request: Request):
	req_body = await request.json()
	print(req_body)
	command = req_body["cmd"]
	cmd_data = req_body["content"]
	if command == "eat_mem" :
			#mtoken = request.cookies.get("memory_token")
			mtoken = cmd_data["memory_token"]
			if mtoken==None:
				return JSONResponse(content = {"content":"login error"})
			token_stat = authToken(mtoken)

			if token_stat == True:
				print("using cookie ",mtoken)
				if mtoken!=None:
					rst = awaddmem(mtoken,cmd_data)
					return JSONResponse(content = rst)
				else:
					return JSONResponse(content = {"status":200,"message":"request error"})
			else:
				res_err = {"content":"404 user not found please, reload", "status":404}
				return JSONResponse(content = res_err)
	elif command == "eat_user":
			usr_data = "user created"
        	#eatUser(cmd_data)
			user_man = awcreatedb(cmd_data)

			if user_man !=None:
					usr_json = {"content":usr_data,"memory_token":user_man}
					response = JSONResponse(content = usr_json,)
					#response.set_cookie(key="memory_token",=user_man)
					print(f"using cookie: {usr_json}")
					return response
			else:
				err_data = "user failed"
				err_json = {"content":err_data}
				return JSONResponse(content = err_json)
                  #return context.res.json(err_json, 200)

	elif command == "buff_mem":
					mtoken = cmd_data["memory_token"]
					#request.cookies.get("memory_token")
					print(mtoken)
					token_stat = authToken(mtoken)
					print("token okay")
					if(token_stat==True):
						#my_prompt = gptEat(mtoken,cmd_data)
						#print("\neating my prompt: ",my_prompt)
						#prompt_dta = handlePrompt(mtoken,my_prompt)
						made_anss = execPrompt(mtoken,cmd_data)
						#print(f"\n\n\t\tanswers are: {made_ans}")
						prompt_dta = ''
						if len(made_anss) == 0:
							tprompt_dta = {"ok": True, "content": "no content, please add a memory"}
							return JSONResponse(content = tprompt_dta)
						for made_ans in made_anss:
							#mem_err = made_ans['content'].find("<mem_error_502>")
							mem_err = -1
							if mem_err == -1:
								prompt_dta = made_ans
								break
						if len(prompt_dta) == 0:
							prompt_dta == parseMem(made_anss[0])
						if prompt_dta["ok"]==True:
							return JSONResponse(content = prompt_dta)
						else:
							err_data = {"content":"prompt error"}
							return JSONResponse(content = err_data)
					else:
						res_err = {"content":"404 user not found please, reload", "status":404}
						return JSONResponse(content = res_err)
	elif command == "eat_url":
					mtoken = cmd_data["memory_token"]
		#request.cookies.get("memory_token"
					print(mtoken)
					token_stat = authToken(mtoken)
					print("token okay")
					if token_stat == True:
						print("authenticated")
						eat_stat = urlEater(mtoken,cmd_data)

						if eat_stat == True:
							tprompt_dta = {"ok":True,"content":"memory noted"}
							return JSONResponse(content = tprompt_dta)
						else:
							err_data = {"ok":False,"content":"memory error"}
							return JSONResponse(content = err_data)
					else:
						print("authentication failed")
						res_err = {"content":"404 user not found please, reload", "status":404}
						return JSONResponse(content = res_err)


			#else:
			#		err_data = {"content":"user failed"}
			#		return JSONResponse(content = err_data)
                #return context.res.json(err_data, 200)
