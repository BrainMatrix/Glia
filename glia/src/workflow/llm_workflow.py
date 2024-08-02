import asyncio

from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY

from glia.src.service.llm_service import LLMService
from glia.src.schedule.schedule import Schedule



class LLMWorkflow(BaseWorkflow):
    """LLMWorkflow Class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #self.resource_manager = self.resource_manager
        #self.schedule=self.schedule
        #self.service_priority = self.service_priority
        #self.process_result = None
        
    #    if self.service is None:
    #        self.service = LLMService(
    #            name="LLMService",
    #            call_model_name='OPENCHAT',
    #            resource_manager=self.resource_manager,
    #        )
    #    else:
    #        if isinstance(self.service, LLMService):
    #            pass

    async def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """
        
       # print(
       #     f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}, start ..."
       # )
       # await asyncio.sleep(1)
        self.schedule.llm_service_queue.put(self.service_priority)#将自己的优先级传入优先级队列中
        
        await asyncio.sleep(10)#保证在进行队首出队时，所有线程的消息均已插入消息队列
        
        #print(self.schedule.llm_service_queue.qsize())
        
        while True:
            #当前workflow陷入阻塞
            if self.service_priority == self.schedule.llm_service_queue.check_head_element():
                break
        
        #优先级队列队首元素是自己，开始调用service执行
        self.service = LLMService(  #self.service是一个对象，不可以在使用的时候再创建，而单纯数据self.pre_result就可以在使用它的时候再创建
                name="LLMService",
                call_model_name="OPENCHAT",
                resource_manager=self.resource_manager,
            )
        
        self.process_result = await self.service(self.prev_result)
       # print(
       #     f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}, end ..."
       # )
        self.schedule.llm_service_queue.get()#等到service服务执行完毕时，再将其请求从优先级队列中取出
       


    def set_branch(self, branch_name):
        self.branch_name=branch_name
        self.branch_list[self.branch_name] = LLMWorkflow(
            name=self.name,#直接引用
            service_priority=self.service_priority,#直接引用
            resource_manager=self.resource_manager,#直接引用
            schedule=self.schedule, #直接引用
        )
        self.branch_list[self.branch_name].sub_workflows = {key: wf.set_branch() for key, wf in self.sub_workflows.items()}#深拷贝，不是引用
        #self.branch_list[self.branch_name].branch_list = {key: wf.clone() for key, wf in self.branch_list.items()}#复制还是置None?
        self.branch_list[self.branch_name].branch_list = {} #置空
        self.branch_list[self.branch_name].process_result = None #该参数不能引用