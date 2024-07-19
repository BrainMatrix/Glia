import asyncio

from .base_service import BaseService


class OCRService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing service {self.name} with resources: {self.call_model_resource}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.call_model(self.prev_result)
        print(
            f"Executing service {self.name} with resources: {self.call_model_resource}, end ..."
        )
        return self.process_result
