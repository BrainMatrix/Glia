from typing import List, Dict, Any
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

from glia.src.schedule.schedule import Schedule
from concurrent.futures import ThreadPoolExecutor
from monitor_man_falls_workflow import monitor_man_falls_workflow


class TestAIWorkflow(BaseWorkflow):
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
        name: Enum = None,
        resource_manager: ResourceManager = None,
        schedule: Schedule = None,
        llm_service_priority: int = None,#以下三个参数是base_workflow所不具有的
        sr_service_priority: int = None,
        tts_service_priority: int = None,
    ):
        """Constructor method
        """
        super().__init__(
            name=name,
            resource_manager=resource_manager,
            schedule=schedule,
        )
        self.resource_manager: ResourceManager = resource_manager
        self.schedule: Schedule = schedule
        self.llm_service_priority: int = llm_service_priority
        self.sr_service_priority: int = sr_service_priority
        self.tts_service_priority: int = tts_service_priority
        
        self.llm_agent_workflow = LLMWorkflow(
            name=WorkflowName.LLM,
            service_priority=self.llm_service_priority,
            resource_manager=self.resource_manager,
            schedule=self.schedule,
        )
        
        self.sr_workflow = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,
            service_priority=self.sr_service_priority,
            resource_manager=self.resource_manager,
            schedule=self.schedule,
        )
        
        self.tts_workflow = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            service_priority=self.tts_service_priority,
            resource_manager=self.resource_manager,
            schedule=self.schedule,
        )
    
        self.add_sub_workflow(
           self.sr_workflow, self.llm_agent_workflow, self.tts_workflow
        )

    async def __call__(self, input):
        """Accept input, call the 'run' method to asynchronously run the entire algorithm workflow, and return the final result.

        :param input: Input
        :type input: Any
        :return: The final execution result of the workflow.
        :rtype: Any
        
        """      
        self.prev_result = input
        await self.run()

        return self.process_result

    async def run(self):
        """Utilize user input to fully run the complete workflow of speech recognition -> LLM -> speech synthesis, and record the computation results.
        
        :param input: Input
        :type input: Any       
        
        """  
        #sr服务的优先级非常重要，因为sr的优先级越高的workflow，它后面的服务队列可以优先插入，别人就算优先级高，但没有插入，导致还是该workflow继续在后面的队列中优先执行
        #所以如果想模拟多个workflow同时申请的情景，则我在workflow插入消息进优先级队列之后，增加await(10)，来使其被迫等待其他所有的workflow都插入了消息进优先级队列
        #综上，影响优先级队列的因素，一个是各个消息自带的优先级，一个就是下面的await的语句的限制
        preprocessed_str = await self.sr_workflow(self.prev_result)
        print(preprocessed_str + str(self.name))
        llm_output = await self.llm_agent_workflow(preprocessed_str)
        print(llm_output + str(self.name))
        self.process_result = await self.tts_workflow(llm_output)
        print(self.process_result + str(self.name))



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
    )

    schedule = Schedule()#初始化4+1个消息优先级队列

    my_workflow = TestAIWorkflow(
        name=WorkflowName.MAIN0, resource_manager=resource_manager, schedule=schedule, llm_service_priority=3, sr_service_priority=1, tts_service_priority=6,
    )

    monitor_workflow = monitor_man_falls_workflow(
        name=WorkflowName.Monitor, resource_manager=resource_manager, schedule=schedule
    )   
    
   #添加一个新TestAIWorkflow
   
    Test_workflow = TestAIWorkflow(
       name=WorkflowName.MAIN1, resource_manager=resource_manager, schedule=schedule, llm_service_priority=1, sr_service_priority=3, tts_service_priority=1,
    )
    
    Test_workflow2 = TestAIWorkflow(
       name=WorkflowName.MAIN2, resource_manager=resource_manager, schedule=schedule, llm_service_priority=5, sr_service_priority=2, tts_service_priority=2,
    )
    
    Test_workflow3 = TestAIWorkflow(
       name=WorkflowName.MAIN3, resource_manager=resource_manager, schedule=schedule, llm_service_priority=4, sr_service_priority=4, tts_service_priority=3,
    )
     

   # asyncio.run(my_workflow("hello"))#调用魔法函数_call_


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
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [ executor.submit(run_asyncio_in_thread, loop, workflow, param) for (workflow, param), loop in zip(workflows, loops)  ]
        #如果我们往线程池里面丢了两个loop，但是只设置了一个线程，那么这两个loop的执行是顺序执行还是也可以异步？
        print("len(futures)", len(futures))
        for future in futures:
            future.result()
            
    #print(my_workflow.print_resource_strategy()) 
            
    #关闭所有loop
    for loop in loops:
        loop.close()

       
  
  #ending.......
  
  

 
