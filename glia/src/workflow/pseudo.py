from typing import List, Dict, Any, Union
import importlib
import logging
from enum import Enum
import asyncio
import threading
import time


from glia.src.workflow import WorkflowName
from glia.src.workflow import BaseWorkflow
from glia.src.workflow import LLMWorkflow
from glia.src.workflow import SpeechRecognitionWorkflow
from glia.src.workflow import SpeechSynthesisWorkflow
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.resource.resource import Resource
from glia.src.resource.resource_manager import ResourceManager
from glia.src.workflow import vllm_workflow

from glia.src.schedule.schedule import Schedule
from concurrent.futures import ThreadPoolExecutor
import copy


class TestAIWorkflow(BaseWorkflow):#这个类是包装的多个workflow产生的flow工作流
    """This is a complete AI algorithm workflow composed of multiple workflows that can achieve speech recognition -> LLM -> speech synthesis.
    
    :param name: The name of the workflow to which the algorithm belongs, defaults to None
    :type name: Enum
    :param resource_manager: Instance object of the ResourceManager, defaults to None
    :type resource_manager: class:'ResourceManager'
    :param schedule: Priority of the workflow.
    :type schedule: class:'Schedule'
    
    """

    def __init__(
        self,
        name: Enum = None,#不建议枚举，建议str
        schedule: Schedule = None,
        #llm_service_priority: int = None,#以下三个参数是base_workflow所不具有的
        #sr_service_priority: int = None,#这个地方的服务优先级不适合这样写死，因为后面如果你调用其他的workflow，你的优先级该写在哪里？
        #tts_service_priority: int = None,
        #all_service_priority: Dict[BaseWorkflow, int] = None,#用来动态添加或删除
        #优先级是用户在实例化worflow的时候传参进去
        *args, **kwargs
    ):
        """Constructor method
        """
        super().__init__(
            name=name,
            schedule=schedule,
        )
        self.schedule: Schedule = schedule
        self.name = name
        self.last_workflow: BaseWorkflow = None#这个属性，只有flow才有意义,且目前只允许一个last_workflow存在
        self.first_workflow: BaseWorkflow = None#这个属性，只有flow才有意义，且目前只允许一个first_workflow存在
        #self.llm_service_priority: int = llm_service_priority
        #self.sr_service_priority: int = sr_service_priority
        #self.tts_service_priority: int = tts_service_priority
        
     
        
    #    self.sr_workflow = SpeechRecognitionWorkflow(
    #        name=WorkflowName.SPEECH_RECOGNITION,
    #        service_priority=self.sr_service_priority,
    #        #resource_manager=self.resource_manager,
    #        schedule=self.schedule,

    #    )
    #    self.llm_agent_workflow = LLMWorkflow(
    #        name=WorkflowName.LLM,
    #        service_priority=self.llm_service_priority,
            #resource_manager=self.resource_manager,
    #        schedule=self.schedule,
    #        needs=[self.sr_workflow],
    #    )
        
    #    self.tts_workflow = SpeechSynthesisWorkflow(
    #        name=WorkflowName.TEXT_TO_SPEECH,
    #        service_priority=self.tts_service_priority,
            #resource_manager=self.resource_manager,
    #        schedule=self.schedule,
    #        needs=[self.llm_agent_workflow],
    #    )
    
    #    self.add_sub_workflow(
    #       self.sr_workflow, self.llm_agent_workflow, self.tts_workflow
    #    )
       # self.schedule.llm_service_queue.put(self.llm_service_priority)
       # self.schedule.speech_recognition_service_queue.put(self.sr_service_priority)
       # self.schedule.speech_synthesis_service_queue.put(self.tts_service_priority)
    def build_nexts(self):#前提是已经构建好sub_workflow列表,以及needs列表
        for workflow in self.sub_workflows:
            if not workflow.needs == []:
                for need_workflow in workflow.needs:
                    need_workflow.nexts.append(workflow)
       
    def add_sub_workflow(self, *sub_workflows):#该函数使用的条件是，add的workflow的needs都已经设置好了，大多数是用于初次构建flow的时候调用
    #可以加一个当前workflow是否在sub_workflow字典里的判定
        for workflow in sub_workflows:#子workflow的添加，不涉及其结构，随意添加进字典即可，结构体现在workflow的needs属性上
           #if workflow in self.sub_workflows:
               #抛出异常，显示该workflow已经存在
           #    pass
           #else:                  
            self.sub_workflows.append(workflow) 
           
        self.build_nexts()
        
        for workflow in self.sub_workflows:
            if workflow.nexts == []:
               self.last_workflow = workflow
            if workflow.needs == []:
               self.first_workflow = workflow
        #flow的依赖项需要与first,last的workflow保持同步更新，即下面的两句话让它们指向同一块内存地址      
        #self.needs = self.first_workflow.needs
        #self.nexts = self.last_workflow.nexts
        #禁止设置flow的依赖项，无任何意义
        
        
    
       
    
    def insert_workflow_at_tail(self,workflow:BaseWorkflow):#允许插入一个单workflow，不允许插入一个完整的flow
        #需要修改原来最后的workflow和插入的workflow的某些属性值,插入只允许以workflow为单位插入，无法插入一个flow       
        workflow.needs.append(self.last_workflow)
        self.last_workflow.nexts.append(workflow)
        self.last_workflow = workflow
        self.sub_workflows.append(workflow)
        
    def insert_workflow_at_head(self,workflow:BaseWorkflow):#允许插入一个单workflow，不允许插入一个完整的flow
        workflow.nexts.append(self.first_workflow)
        self.first_workflow.needs.append(workflow)
        self.first_workflow = workflow
        self.sub_workflows.append(workflow)
        
    def insert_workflow_at_middle(self,workflow_above:Union[List[BaseWorkflow], BaseWorkflow],workflow_below:Union[List[BaseWorkflow], BaseWorkflow],workflow:BaseWorkflow):
        #允许插入一个单workflow，不允许插入一个完整的flow
        workflow.nexts.append(workflow_below)

        if type(workflow_above) == List and len(workflow_above) > 1 and type(workflow_below) == List and len(workflow_below) > 1:
           for workflows in workflow_above:
               workflow.needs.append(workflows)
               workflows.nexts  
       
        workflow.needs.append(workflow_above)
        workflow_above.nexts

    def __call__(self, input:any):
         #特别特别注意，嵌套workflow的self.prev_result一定是在它的self.sub_workflow组成的拓扑图中的起始输入数据
        self.prev_result.append(input) #这里默认整个flow的用户输入是一个str类型数据，而不是一个列表

        self.execute()
        #self.run()

        return self.process_result

    def execute(self):#设计为只能作为拓扑的sub_workflow集合的执行函数
        """Utilize user input to fully run the complete workflow of speech recognition -> LLM -> speech synthesis, and record the computation results.
        
        :param input: Input
        :type input: Any       
        
        """  
        #sr服务的优先级非常重要，因为sr的优先级越高的workflow，它后面的服务队列可以优先插入，别人就算优先级高，但没有插入，导致还是该workflow继续在后面的队列中优先执行
        #所以如果想模拟多个workflow同时申请的情景，则我在workflow插入消息进优先级队列之后，增加await(10)，来使其被迫等待其他所有的workflow都插入了消息进优先级队列
        #综上，影响优先级队列的因素，一个是各个消息自带的优先级，一个就是下面的await的语句的限制
        
        #with self.schedule.sr_queue_head_element:值得注意的是，对队列的放和进，不用加锁是因为4个线程是并发的，即某一时刻只有一个线程在执行
        #self.schedule.speech_recognition_service_queue.put(self.sr_service_priority)
        #await asyncio.sleep(10)#模拟一个同一时刻申请相同服务的多线程操作
        all_finished_workflow_in_a_level: List[BaseWorkflow] = []
        record_workflow: List[BaseWorkflow] = []
        
        #这个地方我进行了修改，删除了深拷贝
        #self.first_workflow.prev_result = copy.deepcopy(self.prev_result)
        self.first_workflow.prev_result = self.prev_result
        self.first_workflow(self.first_workflow.prev_result)#这里默认嵌套workflow的开头只有一个workflow，不考虑多个开头workflow的情况
       # print(self.first_workflow.process_result + str(self.name))
        all_finished_workflow_in_a_level.append(self.first_workflow)        
                
           
        while True:
            if len(all_finished_workflow_in_a_level) == 1 and all_finished_workflow_in_a_level[0].nexts == []:#不允许有多个结尾workflow的存在，我们这个框架只允许开头有一个workflow，结尾也只有一个workflow，中间部分的拓扑结构则随便
                self.process_result = all_finished_workflow_in_a_level[0].process_result
                break
            elif len(record_workflow) == 1 and record_workflow[0].nexts == []:
                self.process_result = record_workflow[0].process_result
                break
            else:
                if not all_finished_workflow_in_a_level == [] and record_workflow == []:
                   for finished_workflow in all_finished_workflow_in_a_level:
                       for workflow in finished_workflow.nexts:
                           if workflow.is_needs_all_finished:#这里可能会产生阻塞
                               workflow.prev_result.append(finished_workflow.process_result)#这里的pre_result应该设置为一个列表，因为有可能有多个输入
                               if len(workflow.prev_result) == len(workflow.needs):#当前workflow的所有依赖项都将执行结果传送给它
                                  workflow.process_result = workflow(workflow.prev_result)
                                  #print(workflow.process_result + str(self.name))
                                  record_workflow.append(workflow)
                   all_finished_workflow_in_a_level.clear()  
                               
                elif all_finished_workflow_in_a_level == [] and not record_workflow == []:
                   for finished_workflow in record_workflow:
                       for workflow in finished_workflow.nexts:
                           if workflow.is_needs_all_finished:#这里可能会产生阻塞,这个判定可能不是很必须
                               workflow.prev_result.append(finished_workflow.process_result)#这里的pre_result应该设置为一个列表，因为有可能有多个输入
                               if len(workflow.prev_result) == len(workflow.needs):#当前workflow的所有依赖项都将执行结果传送给它
                                  workflow.process_result = workflow(workflow.prev_result)
                                  #print(workflow.process_result + str(self.name))
                                  all_finished_workflow_in_a_level.append(workflow)
                   record_workflow.clear() 
                
                else:
                    #显示异常错误
                    pass             
                   
        
        #preprocessed_str = await self.sr_workflow(self.prev_result)
        #print(preprocessed_str + str(self.name))
        
        #with self.schedule.llm_queue_head_element:
        #self.schedule.llm_service_queue.put(self.llm_service_priority)
        #await asyncio.sleep(10)
        #未考虑依赖项的影响
        #llm_output = await self.llm_agent_workflow(preprocessed_str)
        #print(llm_output + str(self.name))
        #with self.schedule.tts_queue_head_element:
        #await asyncio.sleep(10)
        #self.process_result = await self.tts_workflow(llm_output)
        #print(self.process_result + str(self.name))
        #上面的子workflow的执行，也不能这样写死的执行，因为一旦你添加了新的workflow，那你还得修改这个类文件吗？
        



def run_asyncio_in_thread(loop, workflow, *args):
    
    asyncio.set_event_loop(loop)#给当前线程分配loop,避免线程之间共享loop
    try:
        result = loop.run_until_complete(workflow(*args))#该函数的功能与asyncio.run(my_workflow("hello"))一致，但是如果使用loop这个接口，则必须先建立一个loop才行，而asyncio.run不需要
    finally:
        loop.stop()
    return result #return的结果给了future


if __name__ == "__main__":

    resource_manager = ResourceManager()

    resource_manager.register_model_list(#模型注册只需要注册一次，注册后未来所有使用该模型的不同workflow都是按照这个注册信息来进行allocate资源的分配
        {
            "Whisper": Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
            "Parseq": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0]),
            "OPENCHAT": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[1, 2]),
            "CHATTTS": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[3, 4]),
        }
    )#model不能写死，需要提供一个一般模型的接口，这里的注册操作注册的都是已经写死的model的资源注册

    schedule = Schedule(resource_manager=resource_manager)#初始化4+1个消息优先级队列
   
   # my_workflow = TestAIWorkflow(
   #     name=WorkflowName.MAIN0, schedule=schedule, llm_service_priority=3, sr_service_priority=1, tts_service_priority=6,
   # )

   # monitor_workflow = monitor_man_falls_workflow(
   #     name=WorkflowName.Monitor, resource_manager=resource_manager, schedule=schedule
   # )   
    
   #添加一个新TestAIWorkflow
   
   # Test_workflow = TestAIWorkflow(
   #    name=WorkflowName.MAIN1, schedule=schedule, llm_service_priority=1, sr_service_priority=3, tts_service_priority=1,
   # )
    
   # Test_workflow2 = TestAIWorkflow(
   #    name=WorkflowName.MAIN2, schedule=schedule, llm_service_priority=5, sr_service_priority=2, tts_service_priority=2,
   # )
    
   # Test_workflow3 = TestAIWorkflow(
   #    name=WorkflowName.MAIN3, schedule=schedule, llm_service_priority=4, sr_service_priority=4, tts_service_priority=3,
   # )
    sr_workflow = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,#不建议搞成enum的形式，因为调用子workflow的时候，会发生重名的现象
            service_priority=1,
            #resource_manager=self.resource_manager,
            schedule=schedule,
        )
    llm_agent_workflow = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=3,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[sr_workflow],
        )
        
    tts_workflow = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            service_priority=6,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[llm_agent_workflow],
        )  
    
    my_workflow = TestAIWorkflow(name=WorkflowName.MAIN0, schedule=schedule)
   # my_workflow.add_sub_workflow(sr_workflow, llm_agent_workflow, tts_workflow)
    my_workflow.add_sub_workflow(llm_agent_workflow, tts_workflow,sr_workflow)
    sr_workflow1 = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,#不建议搞成enum的形式，因为调用子workflow的时候，会发生重名的现象
            service_priority=3,
            #resource_manager=self.resource_manager,
            schedule=schedule,
        )
    llm_agent_workflow1 = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=1,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[sr_workflow1],
        )
        
    tts_workflow1 = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            service_priority=1,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[llm_agent_workflow1],
        )  
    Test_workflow = TestAIWorkflow(name=WorkflowName.MAIN1, schedule=schedule)
    #Test_workflow.add_sub_workflow(sr_workflow1, llm_agent_workflow1, tts_workflow1)
    Test_workflow.add_sub_workflow(llm_agent_workflow1, sr_workflow1, tts_workflow1)
    sr_workflow2 = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,#不建议搞成enum的形式，因为调用子workflow的时候，会发生重名的现象
            service_priority=2,
            #resource_manager=self.resource_manager,
            schedule=schedule,
        )
    llm_agent_workflow2 = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=5,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[sr_workflow2],
        )
        
    tts_workflow2 = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            service_priority=2,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[llm_agent_workflow2],
        )  
    
    Test_workflow2 = TestAIWorkflow(name=WorkflowName.MAIN2,schedule=schedule)
    #Test_workflow2.add_sub_workflow(sr_workflow2, llm_agent_workflow2, tts_workflow2)
    Test_workflow2.add_sub_workflow(sr_workflow2, tts_workflow2,llm_agent_workflow2)
    
    sr_workflow3 = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,#不建议搞成enum的形式，因为调用子workflow的时候，会发生重名的现象
            service_priority=4,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[],#这个一定要写上，不然容易出bug
        )
    llm_agent_workflow3 = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=4,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[sr_workflow3],
        )
        
    tts_workflow3 = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            service_priority=3,
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[llm_agent_workflow3],
        )
    
    Test_workflow3 = TestAIWorkflow(name=WorkflowName.MAIN3, schedule=schedule)
    #Test_workflow3.add_sub_workflow(sr_workflow3, llm_agent_workflow3, tts_workflow3,)
    Test_workflow3.add_sub_workflow(tts_workflow3, llm_agent_workflow3, sr_workflow3)
   
    #插入一个workflow在 Test_workflow3的尾部
    
    llm_agent_workflow4 = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=1,#注意，这里的优先级与上面llm_agent_workflow3的优先级无任何关联，谁大谁小都没关系
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[],
        )#插入的workflow不定义暂时不需要用户定义其needs与nexts
    
    Test_workflow3.insert_workflow_at_tail(llm_agent_workflow4)
    #asyncio.run(my_workflow("hello"))#调用魔法函数_call_
    #asyncio.run(Test_workflow3("test3"))
    
    #插入一个workflow在flow的头部
    llm_agent_workflow5 = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=1,#注意，这里的优先级与上面llm_agent_workflow3的优先级无任何关联，谁大谁小都没关系
            #resource_manager=self.resource_manager,
            schedule=schedule,
            needs=[],
        )
    
    
    Test_workflow3.insert_workflow_at_head(llm_agent_workflow5)
    
    #RPBot测试
    
    RPBot_flow = TestAIWorkflow(name=WorkflowName.RPBot, schedule=schedule)
    
    vllm_test_workflow = vllm_workflow(name=WorkflowName.VLLM,
            service_priority=1,
            schedule=schedule,
            needs=[],)
    
    
    

    workflows = [
       (my_workflow, "hello"),
       (Test_workflow, "test"),
       (Test_workflow2, "test2"),
       (Test_workflow3, "test3"),
   ]
    #下面语句把workflows列表中的两个workflow封装成两个loop
    #一个loop内的事件之间实现并发操作，而不同loop之间是实现的并行即多线程执行。
    #在下面这个loops中，形成了两个loop,它们彼此之间可以实现多线程执行，但是在单独的loop内部，由于我们只包含了一个workflow，因此无法实现loop内的并发操作
    #在同一时刻，一个线程只能运行一个loop，也就是说，“并发”这个操作是一个线程实现的，而“并行”操作是需要多个线程存在即多个loop存在才有意义。
    loops = [asyncio.new_event_loop() for _ in workflows]#new_event_loop的作用是创建一个新的loop，新loop不会与现有的loop产生任何关联
    #上面创建的4个loop，每个loop目前来说，与workflows列表里的内容并无任何关系，仅仅是明确了创建的loop的数量。
    #asyncio.get_event_loop()接口是获取当前执行线程的loop，如果当前线程并没有loop，则它会创建一个新的loop
    
    #并发可以允许事件之间存在依赖关系，与并行不同，任何事件都可以实现并发
    output_list = []#这个List有什么作用吗？
    
    #ThreadPoolExecutor是一个类，下面实例化了该类
    with ThreadPoolExecutor(max_workers=4) as executor:
        #submit()一次只能提交一个线程的任务
        futures = [ executor.submit(run_asyncio_in_thread, loop, workflow, param) for (workflow, param), loop in zip(workflows, loops)  ]#submit的任务数量不需要和max_worker保持一致
        #需要注意的是，不管是向线程池中的多线程提交任务(submit()接口)，还是向一个loop提交工作任务(loop.run_until_complete接口或asyncio.run接口)，传入接口的都是功能函数+其函数传参
        #如果我们往线程池里面丢了两个loop，但是只设置了一个线程，那么这两个loop的执行是顺序执行还是也可以异步？
        print("len(futures)", len(futures))
        for future in futures:#每一个future对象都是submit函数返回的
            future.result()
            
    #print(my_workflow.print_resource_strategy()) 
    
            
    #关闭所有loop
    for loop in loops:
        loop.close()

       
  
  #ending.......
  
  

 
