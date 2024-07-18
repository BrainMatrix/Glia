import asyncio

from .base_service import BaseService


class SpeechRecognitionService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):
        print(
            f"Executing service {self.name} with resources: {self.call_model_resource}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.call_model(self.prev_result)
        print(self.process_result)
        print(
            f"Executing service {self.name} with resources: {self.call_model_resource}"
        )
        return self.process_result
