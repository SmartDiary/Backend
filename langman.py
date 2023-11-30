#from langchain import LLMChain
import tiktoken
from bs4 import BeautifulSoup
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from langchain.llms import OpenAI
from langchain import PromptTemplate


from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.summarize import load_summarize_chain

from langchain.chains import AnalyzeDocumentChain
import time



master_prompt = "'''Below is a list of my memories"

def xeatUrl(url_link):
    loader = WebBaseLoader(url_link)
    data = loader.load()[0].page_content
    #print(data)
    full_text = data
    #open("/content/MyDrive/MyDrive/langdata/state_of_the_union.txt", "r").read()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(full_text)
    try:
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_texts(texts, embeddings)
        template = """Answer the question based only on the following context:\n {context}Question: \n{question}"""
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI()
        chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | model | StrOutputParser())
        retriever = db.as_retriever()
        chat_data = chain.invoke("analyze the context amd explain what it is about")
        link_data = f" The link {url_link} contains the following:  {chat_data}"
        print("\n\n\t")
        print(link_data)
        save_mem(link_data,'')
        print("\tmemory printed")
        return True
    except Exception as ex:
        print(ex)
        return False

def eatUrl(url_link):
    xmem_data = {}
    try:
        loader = WebBaseLoader(url_link)
        #("https://en.wikipedia.org/wiki/Internet_Protocol_version_4")
        #docs = loader.load()
        #print(docs)
        scraper = loader.scrape()
        url_title = (scraper.find('title').text)
        content = scraper.text
        #docs[0].page_content
        textSplitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=8000,chunk_overlap=0)
        text = textSplitter.split_text(content)
        print(text)
        print(len(text))
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        chain = load_summarize_chain(llm, chain_type="stuff")

        summarize_document_chain = AnalyzeDocumentChain(combine_docs_chain=chain, text_splitter=textSplitter)

        sum_text = summarize_document_chain.run(text[0])
        link_data = f" The link {url_link} is about the following:  {sum_text}"
        print("\n\n\t")
        print(link_data)
        #save_mem(link_data,'')
        print("\tmemory printed")
        print("\n\n\t\tURL TITLE IS: ",url_title)
        xmem_data["title"] = url_title
        xmem_data["content"] = link_data
        xmem_data["tags"] = ''
        return xmem_data
    except Exception as ex:
        print(ex)
        return xmem_data



def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def save_mem(memory,old_memories):
    print("prompt_text beginning")
    #mem_template = """The following is a record of my memories, I will later ask you a question about them.\n{old_mems}\nmemory: {mem}"""
    mem_template = """{old_mems} \nmemory: {mem}"""
    print("prompt_text started")
    prompt_template =PromptTemplate(input_variables=["old_mems","mem"],template = mem_template)
    print("prompt_text making")
    prompt_text = prompt_template.format(mem=memory,old_mems=old_memories)
    print("prompt_text created")
    return prompt_text

def recall_mem(memories,qtn):
  print("\n\n\tstarted recall")
  ctrl_prompt = "You are an intelligent personal diary called Katende. You will get input of memories identified by memory:, each memory will have a memory title identified by use_mem_header:, the memory body identified by use_content:'memory_body',tags identified by use_mem_tags:, date tag identified by use_date:'year-month-date' and a time tag identified by use_time in the format hours : minutes: seconds.\nthe use_date and use_time show when the memory was recorded.\nI have Questions that need to be answered about my memories.\nEach question may have a tag ref_date:'year-month-date' and tag ref_time:'hours:minutes:seconds' to show when it was asked.If i ask about date or time, use ref_date, ref_time, use_date, use_time values for any date and time related calculations. Answer the questions with using the memory data in the personal diary."
  #if there is no memory, return your answer with the format <mem_error_502>your_answer</mem_error_502>"
  query_template = """{master_prompt}:\n{mems}\n\nQuestion: {qtn}\n\nAnswer:"""
  prompt = PromptTemplate(input_variables=["qtn","mems","master_prompt"],template = query_template)
  print("\nrecall opened")
  prompt_txt = prompt.format(qtn=qtn,mems=memories,master_prompt=ctrl_prompt)
  print("\nrecall formatted")
  return prompt_txt

def getTokenCount(memory):
    tikencode = tiktoken.encoding_for_model("gpt-3.5-turbo-1106")
    tokens = tikencode.encode(memory)
    return len(tokens)


def build_mem(memories):
    clear_mems = ''
    old_mems = ''
    print(memories)
    #input()
    ctx = 0
    made_mems = []
    for memory in memories:
        #print(f"{ctx} {memory}")
        #if ctx!=20:
        clear_mems = save_mem(memory,old_mems)
        #print("\t\t",clear_mems)
        old_mems += clear_mems
        token_len = getTokenCount(old_mems)
        if(token_len>=10000):
                made_mems.append(old_mems)
                old_mems = ''
        clear_mems = ''
            #ctx=ctx+1
        ctx=ctx+1
    if len(old_mems) > 0:
        print("more mems")
        made_mems.append(old_mems)
    print(f"\n\n\tloop finished: {old_mems}")
    #return old_mems
    return made_mems

def total_recall(memories,query):
    all_memories = build_mem(memories)
    
    print(f"\n\n\tall memories: \n{all_memories}")
    #input()
    made_prompts = []
    for a_memory in all_memories:
        made_prompt = recall_mem(a_memory,query)
        made_prompts.append(made_prompt)
    return made_prompts

def askMem(prompt):
    try:
        openai = ChatOpenAI(temperature = 1,model_name='gpt-3.5-turbo-1106')
        completion = openai.predict(prompt)
        print(completion)
        prompt_json = {"role":"assistant","content":completion}
        json_data= {"ok": True, "content": completion}
        return json_data
    except Exception as ex:
        print(ex)
        json_error = {"ok": False, "content": "Failed to query model."}
        return json_error