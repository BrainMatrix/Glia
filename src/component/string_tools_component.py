import asyncio

from .base_component import BaseComponent

class StringToolsComponent(BaseComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = (
            self.prev_result + ", 字符串成功处理完毕!"
            if self.prev_result
            else "hh" + "字符串成功处理完毕!"
        )
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )
        return self.process_result
