import heapq
import threading
import time
import queue
from glia.src.service.speech_recognition_service import SpeechRecognitionService
from glia.src.resource import Resource, ResourceManager
from glia.src.service.llm_service import LLMService
from glia.src.service.speech_synthesis_service import SpeechSynthesisService
from glia.src.service.vllm_service import VLLMService
import asyncio
from typing import Dict, List, Union, Any, Optional, Set
from glia.src.service.base_service import BaseService
from glia.src.resource.resource import Resource
from glia.src.service.Embedding_service import EmbeddingService
class DynamicPriorityQueue(queue.PriorityQueue):
    """在queue的基础上增加查看队首元素的接口
    """
        
    def check_head_element(self):
         with self.mutex:
            if not self.queue:
                #raise queue.Empty
                return None
            # 返回队首元素
            return self.queue[0]


class Schedule:
    """Priority class
    """
    def __init__(
        self, 
        resource_manager: ResourceManager = None,
        ):     
        self.close: bool = False
        #service的消息队列与service实例化以及锁的创建操作不同，消息队列我们选择动态创建，另外的两个操作我们静态创建
        self.queue: Dict[str, DynamicPriorityQueue] = {'emergency': DynamicPriorityQueue(maxsize=0)}
        self.failed_task: Dict[str,any] = {}
        self.mutex0 = threading.Lock()#读取queue.dict消息队列的锁
        
        self.service_object: Dict[str, BaseService] = {} 
        self.service_Condition_mutex: Dict[str, threading.Condition]= {}
        self.resource_manager: ResourceManager  = resource_manager
        #self.input:str = None
        
        self.instantiate_services_and_set_lock()#静态实例化所有的service以及条件锁
        #上面的str的service，是不区分不同workflow的service的，因为全局shcedule中，实例化的service，永远只有一个，因此只有一个str的统一名字
        
    
    def instantiate_services_and_set_lock(self):
            self.service_object["SpeechRecognitionService"] = SpeechRecognitionService(#这个实例化操作，是放在这里，还是放在下面的create_task里面，等第一个调用该服务的workflow执行的时候再实例化到service_object字典中？
               name="SpeechRecognitionService",
               call_model_name="Whisper",
               resource_manager=self.resource_manager,
            )
            self.service_object["LLMService"] = LLMService(  
                name="LLMService",
                call_model_name="OPENCHAT",
                resource_manager=self.resource_manager,
            )
            self.service_object["SpeechSynthesisService"] = SpeechSynthesisService(
                 name="SpeechSynthesisService",
                 call_model_name='CHATTTS',
                 resource_manager=self.resource_manager,
            )#有消息队列，有锁
            self.service_object["VLLMService"] = VLLMService(
                 name="VLLMService",#针对schedule使用
                 call_model_name='VLLM',#针对该service实例化什么模型使用
                 resource_manager=self.resource_manager,
            )
            self.service_object["EmbeddingService"] = EmbeddingService(
                 name="EmbeddingService",
                 call_model_name='SentenceTransformer',
                 resource_manager=self.resource_manager,
            )
    
            self.service_object["self_model"] = BaseService(resource_manager=self.resource_manager)#无消息队列，无锁
            #把各种一般模型实例化的service只实例化一个
            self.service_object["emergency"] = BaseService(resource_manager=self.resource_manager)#有消息队列，无锁
            
            self.mutex1 = threading.Lock()
            self.mutex2 = threading.Lock()
            self.mutex3 = threading.Lock()
            self.mutex4 = threading.Lock()
            self.mutex5 = threading.Lock()
            self.service_Condition_mutex["SpeechRecognitionService"] = threading.Condition(self.mutex2)
            self.service_Condition_mutex["LLMService"] = threading.Condition(self.mutex1)
            self.service_Condition_mutex["SpeechSynthesisService"] = threading.Condition(self.mutex3)
            self.service_Condition_mutex["VLLMService"] = threading.Condition(self.mutex4)
            self.service_Condition_mutex["EmbeddingService"] = threading.Condition(self.mutex5)
    
    
   
              
    
    def create_task(self, service_name:str, service_priority:int, input:any):#输入的数据类型为any
        
        if self.close:
            raise Exception("schedule is closed already!")#抛出异常并退出接口
        
        #将输入的列表中的多个信息转化为workflow能处理的单个信息
        #self.input = input[0]#测试阶段，先不考虑多个输入信息的情况
        
        if service_name == "emergency":#涉及不同service之间的竞争
           return self.emergency_event(service_priority, input)#调用紧急事件接口
        
        with self.mutex0:#操作这个队列字典，是一定要加上锁的
          if service_name in self.queue:
              self.queue[service_name].put(service_priority)
          else:
              self.queue[service_name] = DynamicPriorityQueue(maxsize=0)
              self.queue[service_name].put(service_priority)
        
        #self.speech_recognition_service_queue.put(service_priority)#对于优先级队列的读取操作，需要加锁吗？
       
            
        
        if service_name in self.service_object and service_name in self.service_Condition_mutex:
         try:
            with self.service_Condition_mutex[service_name]:#这个锁得是所有线程共享的全局锁。有个问题，如果是多个workflow同时申请，那谁先获得这个锁进行优先级判断呢？
               while True:
                   if service_priority == self.queue[service_name].check_head_element():
                       output = self.service_object[service_name](input)#在考虑这里可以让传参种类变多吗，因为我们是只对workflow之间的传参有限制为一个，但是对service的call的传参并没有要求，
                       #我们是否可以通过workflow的初始化的时候，来进行api_key等信息的传入，也能保证workflow的call的接口只有message一个参数
                       self.queue[service_name].get()
                       self.service_Condition_mutex[service_name].notify_all()
                       break
                   else:
                       self.service_Condition_mutex[service_name].wait()#这个算workflow的中断操作吗
         except Exception as e:
             self.failed_task[service_name] = input
             output = None
             print(f"发生了一个异常: {e}")
             
        
        else:
            pass #抛出异常          
            
                
        return output
    
    def create_self_task(self, model_name:str, model_path:str, model_resource:Resource, input:any):#这个接口专门接收用户自己提供的不同model的服务申请
        #对于一般model，没有创建对应的消息队列，未考虑多个worflow同时申请同一个model_Path的情况。
        if self.close:
            raise Exception("schedule is closed already!")
        
        
        return self.service_object["self.model"].call_self_model(model_name, model_path, model_resource, input)
    
    
    def emergency_event(self, service_priority:int, input:any):
        #也有消息队列，不同workflow之间的紧急事件也存在优先级，所以还是需要状态锁的
        if self.close:
            raise Exception("schedule is closed already!")
        
        self.queue["emergency"].put(service_priority)
        #挂起其他的service，但是已经启动的service无法中断，我们这里的挂起其他service,应该是指暂停所有消息队列中的消息的执行
        
        pass
        #执行完紧急队列中的所有消息，再唤醒挂起的其他service
        pass
    
        return output
    
    
    def close(self):
        #除了已经在执行的service消息，停止所有消息队列中的所有未处理消息的等待执行
        self.queue.clear()
        self.close = True
    
    
    
   

        
    


            
    
