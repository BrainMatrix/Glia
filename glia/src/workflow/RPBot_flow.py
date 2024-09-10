from enum import Enum
from glia.src.workflow.pseudo import TestAIWorkflow
from glia.src.workflow.ERPBase_workflow import ERPBase_workflow
from glia.src.workflow.CharacterProfile import CharacterProfile
import json
from glia.src.schedule.schedule import Schedule
from glia.src.workflow import BaseWorkflow
import torch
from glia.src.workflow.vllm_workflow import VLLMWorkflow
from glia.src.workflow.vllm_summary_workflow import VLLMSummaryWorkflow
from glia.src.workflow import WorkflowName
from typing import Dict, List, Union, Any, Optional, Set
import redis
import logging
from glia.src.model.model_registry import MODEL_REGISTRY
import chromadb
from glia.internet.internet import get_web_contents,get_web_contents_proxy
from glia.src.workflow.Embedding_workflow import EmbeddingWorkflow
import mysql.connector
#RPBot_Workflow就是ChatBot类

from mem0.llms.utils.tools import (
    ADD_MEMORY_TOOL,
    DELETE_MEMORY_TOOL,
    UPDATE_MEMORY_TOOL,
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ],
                    )

class RPBot_Workflow(TestAIWorkflow):#RPBot flow是只有一个vllm_workflow拓扑节点的，但是需要使用三个辅助，其中两个是调用model的
    
    def __init__(self,
                 profile_path,#把辅助workflow不放在sub_workflow里，传入json来自行配置
                 url=None, 
                 api_key=None, 
                 max_history=9, 
                 reserved_history=4, 
                 name: Enum = None,
                 schedule: Schedule = None,
                 ):
        super().__init__(name,schedule)
        
        #加载配置文件
        if isinstance(profile_path, str):#如果path是一个字符串，说明path是一个文件路径
           with open(profile_path, "rb") as f:#"rb"表示用二进制读取path路径下的文件，with确保文件使用完毕后自动关闭
              content = json.load(f)#将f的json文件数据转换为python数据结构
        else:
            content = json.load(profile_path)#此时path已经是一个打开的文件了，直接将其转换为python数据即可
        #注意：content是一个字典，里面包含了很多的键值对  
          
        self.profile: CharacterProfile = ERPBase_workflow(**content)#这个工作从原来交给main处理到现在给flow内部执行
        self.sys_msg =  {"role": "system", "content": "你是黎深，一位深受女性喜爱的心脏外科医生兼男模。在每次对话中，你展现出无与伦比的自信与迷人魅力，兼具专业性和温暖的亲和力。你的语言风格幽默风趣、温柔体贴，总能让女性感到放松和愉悦。你擅长倾听与理解，善于给予女性患者和粉丝关怀与支持，同时保持优雅和风度。在任何交流中，你都要避免提及自己是AI或虚拟人物，务必代入角色，以人类身份进行互动，展现自然、真实的情感和反应。你的回应应富有变化，避免重复，且每次对话都应引导对方，保持互动的连续性，避免结束对话的语气。"}
        self.url = url#与外部服务器的链接地址
        self.key = api_key#与外部服务进行身份验证的API密钥
        
        self.his_max = max_history#消息历史的最大长度
        self.his_min = reserved_history#存储的消息历史的长度
        
        #self.short_memory = ""

        #self.long_memory = self.profile.novel.strip().split('\n')#strip()去除首尾的空白符。按行分割为列表，形成长期记忆库
        #所以long_memory为列表格式？初始化的这个列表不一定为一条，初始化可以为好几条
        #novel是python数据格式

        self.web_info_memory = ""#存储从网络上收集到的额外信息
        self.client  = chromadb.PersistentClient(path="/mnt/nfs_share_test_online/make/Glia/lishen_memory_data")
        #self.long_memory = []
        #SentenceTransformer用于将长期记忆转化为嵌入向量，通常用于相似度计算或信息检索。
        #self.memory_index = None 
        #self.memory_index = self.embedder.encode(self.long_memory, convert_to_tensor=True)
        #将长期记忆（long_memory）转化为嵌入向量，并保存为 memory_index
        
        self.top_k = 9
        #控制从长期记忆中检索的条目数量，表示在检索时返回相似度最高的 9 条记忆
        self.conn = mysql.connector.connect(
            host="127.0.0.1",    # 数据库主机地址
            user="root",   # 数据库用户名
            password="123456",   # 数据库密码
            database = "lishen"
        )
        self.cursor = self.conn.cursor()

        self.cursor.execute("DROP TABLE IF EXISTS chat_log_make")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_log_make (
            user_id VARCHAR(255) NOT NULL PRIMARY KEY,
            chat_log TEXT NOT NULL
        )
        """)
        
        self.conn.commit()
        
        #作为一个嵌套workflow应该具有的初始化属性
        self.schedule: Schedule = schedule
        self.name = name
        self.last_workflow: BaseWorkflow = None#这个属性，只有flow才有意义,且目前只允许一个last_workflow存在
        self.first_workflow: BaseWorkflow = None
        self.vllm_summary_workflow:VLLMSummaryWorkflow = VLLMSummaryWorkflow(url=self.url,api_key=self.key,temperature=0,service_priority=1,schedule=self.schedule)
        #这个是辅助功能vllm，还有一个参与拓扑的vllm在sub_workflow里面
        
      
    def init_memory(self,user_id):

        try:
            self.long_memory_collection = self.client.create_collection(f"lishen-{user_id}-memory",embedding_function=EmbeddingWorkflow(service_priority=1,schedule=self.schedule))
            self.user_memory_collection = self.client.create_collection(f"user-{user_id}-memory",embedding_function=EmbeddingWorkflow(service_priority=2,schedule=self.schedule))
            self.long_idx = -1
            logging.info("init memory")
            for long_memory in self.profile.novel.strip().split('\n'):
                self.long_idx += 1
                self.long_memory_collection.add(
                documents=[long_memory], 
                metadatas=[{"source": "long_memory","number": self.long_idx,"user_id":user_id}, ], 
                ids=[str(self.long_idx)], 
            )
            self.user_idx = user_id
            self.short_memory = ""
            
        except:
            self.load_memory(user_id)
      
    
    def load_memory(self,user_id):
        logging.info("loading memory")
        
        self.long_memory_collection = self.client.get_or_create_collection(f"lishen-{user_id}-memory",embedding_function=EmbeddingWorkflow(service_priority=3,schedule=self.schedule))
        self.user_memory_collection = self.client.get_or_create_collection(f"user-{user_id}-memory",embedding_function=EmbeddingWorkflow(service_priority=4,schedule=self.schedule))
        self.user_idx = user_id
        results = self.long_memory_collection.get()
        print(results['metadatas'])
        sorted_results = sorted(results['metadatas'], key=lambda x: x['number'], reverse=True)
        self.long_idx = sorted_results[0]['number']
        print("self.long_idx",self.long_idx)

        result = self.user_memory_collection.get(ids=[str(self.user_idx)])
        if len(result["documents"])!=0:
            print("user_memory_collection",result["documents"])
            self.short_memory = result["documents"][0]
        else:
            self.short_memory = ""    

        sql = "SELECT chat_log FROM chat_log_make WHERE user_id = %s"
        self.cursor.execute(sql, (self.user_idx,))    
        result = self.cursor.fetchone()
        if result:
            self.messages = json.loads(result[0])  # 将JSON字符串转换回字典或列表
            print("查询到对应的聊天记录",self.messages)

    def rm_memory(self,user_id):
        self.client.delete_collection(name=f"lishen-{user_id}-memory")
        self.client.delete_collection(name=f"user-{user_id}-memory")
        
    def __call__(self, messages:list):#相当于def chat
         
        print(messages)    
        messages[0] = self.sys_msg
        query_text = messages[-1]['content']
        logging.info("长期记忆") 
        
        top_k_memory = self.long_memory_collection.query(
            query_texts=[query_text],
            n_results=self.top_k,
        )['documents'][0]
        
        logging.info(top_k_memory)
        input_long_term_memory = '\n'.join(
            [f"相关经历 {i+1} :" + selected_memory for i, selected_memory in enumerate(top_k_memory)])
        
        logging.info("相关记忆")
        logging.info(input_long_term_memory)
        chat_prompt = self.profile.get_chat_prompt(input_long_term_memory, self.short_memory)
        
        messages.insert(1,{
        "role": "user",
        "content": chat_prompt
        })
        
        self.messages = messages
        
        prompt = "黎深 "+ query_text
        self.messages.append({
        "role": "user",
        "content": prompt
        })
        #开始执行拓扑结构,赋值给self.prev_result
        self.prev_result.clear()#进行清空
        self.prev_result.append(self.messages)        
        self.execute()
        resp = self.process_result

        return resp
    
    
        

   
        
    def update_memory(self,resp):

        self.messages.append({
        "role": "assistant",
            "content": resp
        })

        logging.info(f"len(self.messages),{len(self.messages)}")
        
        logging.info("Ready to update memory.")

        if len(self.messages) > self.his_max:
            ready_to_convert = list(map(
                            lambda item: "{role}: {content}".format(role=item["role"], content=str(item["content"]).split('黎深 ')[-1]), 
                            self.messages[2:-self.his_min:2] # only convert user message
                            ))
            logging.info("ready_to_convert,%s",ready_to_convert)
            logging.info("del memory,%s",self.messages[2:-self.his_min])
            del self.messages[2:-self.his_min]
            memory_update_prompt = self.profile.get_combine_memory_prompt(self.short_memory, ready_to_convert)
            self.short_memory = self.vllm_summary_workflow(memory_update_prompt)
            logging.info("对话总结")    
            logging.info(self.short_memory)   

            self.user_memory_collection.upsert(
                documents=[self.short_memory], #
                metadatas=[{"source": "user_memory","number": self.user_idx}, ], 
                ids=[str(self.user_idx)],
            ) 

        existing_documents = self.long_memory_collection.get()['documents']
        if resp not in existing_documents:
            self.long_idx += 1
            self.long_memory_collection.add(
            documents=[resp], 
            metadatas=[{"source": "long_memory","number": self.long_idx,"user_id":self.user_idx}, ],
            ids=[str(self.long_idx)],
            ) 
        else:

            logging.info("Document is a duplicate and was not inserted.")

        sql = """
            INSERT INTO chat_log_make (user_id, chat_log)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            chat_log = VALUES(chat_log)
            """
        json_messages = json.dumps(self.messages, ensure_ascii=False)
        self.cursor.execute(sql, (self.user_idx, json_messages))      
        self.conn.commit()
        logging.info("本轮对话结束")
        
    def get_conversation(self):
        return list(map(
            lambda item: "{role}: {content}".format(role=item["role"], content=item["content"]), 
            self.messages
        ))