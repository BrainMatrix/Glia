import asyncio

from .base_workflow import BaseWorkflow


class StringToolsWorkflow(BaseWorkflow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resource}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = (
            self.prev_result + ", 字符串成功处理完毕!"
            if self.prev_result
            else "hh" + "字符串成功处理完毕!"
        )
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resource}, end ..."
        )
        return self.process_result
