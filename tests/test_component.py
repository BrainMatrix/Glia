# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import unittest

from src.component import BaseComponent, ComponentName
from src.resource import Resource
from src.model import ModelName
from src.resource import ResourceManager


class MainComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(
            1
        )  # time.sleep Asynchronous blocking  ; asyncio.sleep  Asynchronous non-blocking
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )

class SpeechRecognitionComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)  
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )

class OCRComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )


class StringToolsComponent(BaseComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )


class LLMComponent(BaseComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )


class SpeechSynthesisComponent(BaseComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )


class TestComponent(unittest.TestCase):
    def test_component_execution(self):
        ## init resource manager
        resource_manager = ResourceManager()

        resource_manager.add_model(
            ModelName.Whisper,
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
        )
        # resource_manager.allocate_resources(ModelName.Whisper)
        resource_manager.add_model(
            ModelName.Parseq,
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
        )
        resource_manager.add_model(
            ModelName.OPENCHAT,
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
        )

        resource_manager.add_model(
            ModelName.CHATTTS,
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
        )

        ## build component

        main_component = MainComponent(name=ComponentName.MAIN,
                                       call_model_list=None,
                                       resource_manager=resource_manager,)

        speech_recognition_component = SpeechRecognitionComponent(
            name=ComponentName.SPEECH_RECOGNITION,
            call_model_list=[
                ModelName.Whisper,
            ],
            resource_manager=resource_manager,
        )

        ocr_component = OCRComponent(
            name=ComponentName.OCR,
            call_model_list=[
                ModelName.Parseq,
            ],
            resource_manager=resource_manager,
        )

        string_tools_component = StringToolsComponent(
            name=ComponentName.STRING_TOOLS,
            call_model_list=None,
            resource_manager=resource_manager,
        )
        llm_component = LLMComponent(
            name=ComponentName.LLM,
            call_model_list=[
                ModelName.OPENCHAT,
            ],
            resource_manager=resource_manager,
        )
        speech_synthesis_component = SpeechSynthesisComponent(
            name=ComponentName.TEXT_TO_SPEECH,
            call_model_list=[
                ModelName.CHATTTS,
            ],
            resource_manager=resource_manager,
        )

        main_component.add_sub_component(speech_recognition_component, ocr_component)
        speech_recognition_component.add_sub_component(string_tools_component)
        ocr_component.add_sub_component(string_tools_component)
        string_tools_component.add_sub_component(llm_component)
        llm_component.add_sub_component(speech_synthesis_component)

        # Calling the main component
        asyncio.run(main_component())
        main_component.print_resource_strategy()


if __name__ == "__main__":

    unittest.main()
