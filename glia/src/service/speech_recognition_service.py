import asyncio

from .base_service import BaseService


class SpeechRecognitionService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self):
        print(
            f"Executing service {id(self)} {self.name} with resources: {self.call_model_resource}, start ..."
        )
        self.process_result = self.loop.run_until_complete(
            self.call_model(self.prev_result)
        )
        print(
            f"Executing service {id(self)} {self.name} with resources: {self.call_model_resource}"
        )
        return self.process_result
