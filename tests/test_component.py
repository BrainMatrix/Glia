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
        print(self.process_result)
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
        self.process_result = self.call_model(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}"
        )
        return self.process_result


class OCRComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.call_model(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )
        return self.process_result


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


class LLMComponent(BaseComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.call_model(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )
        return self.process_result


class SpeechSynthesisComponent(BaseComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.call_model(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )
        return self.process_result


class TestComponent(unittest.TestCase):
    def test_component_execution(self):
        ## init resource manager
        resource_manager = ResourceManager()

        # resource_manager.register_model(
        #     ModelName.Whisper,
        #     Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
        # )
        # # resource_manager.allocate_resources(ModelName.Whisper)
        # resource_manager.register_model(
        #     ModelName.Parseq,
        #     Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0, 1]),
        # )
        # resource_manager.register_model(
        #     ModelName.OPENCHAT,
        #     Resource(use_cpu=True, use_gpu=True, use_multi_gpu_ids=[0, 2]),
        # )

        # resource_manager.register_model(
        #     ModelName.CHATTTS,
        #     Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[1, 3]),
        # )

        union_model_resources = {
            ModelName.Whisper: Resource(
                use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]
            ),
            ModelName.Parseq: Resource(
                use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0, 1]
            ),
            ModelName.OPENCHAT: Resource(
                use_cpu=True, use_gpu=True, use_multi_gpu_ids=[0, 2]
            ),
            ModelName.CHATTTS: Resource(
                use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0, 3]
            ),
        }
        resource_manager.register_model_list(union_model_resources)
        ## build component

        main_component = MainComponent(
            name=ComponentName.MAIN,
            call_model_name=None,
            resource_manager=resource_manager,
        )

        speech_recognition_component = SpeechRecognitionComponent(
            name=ComponentName.SPEECH_RECOGNITION,
            call_model_name=ModelName.Whisper,
            resource_manager=resource_manager,
        )

        ocr_component = OCRComponent(
            name=ComponentName.OCR,
            call_model_name=ModelName.Parseq,
            resource_manager=resource_manager,
        )

        string_tools_component = StringToolsComponent(
            name=ComponentName.STRING_TOOLS,
            call_model_name=None,
            resource_manager=resource_manager,
        )

        llm_component = LLMComponent(
            name=ComponentName.LLM,
            call_model_name=ModelName.OPENCHAT,
            resource_manager=resource_manager,
        )

        speech_synthesis_component = SpeechSynthesisComponent(
            name=ComponentName.TEXT_TO_SPEECH,
            call_model_name=ModelName.CHATTTS,
            resource_manager=resource_manager,
        )

        main_component.add_sub_component(speech_recognition_component)
        speech_recognition_component.add_sub_component(string_tools_component)
        # ocr_component.add_sub_component(string_tools_component)
        string_tools_component.add_sub_component(llm_component)
        llm_component.add_sub_component(speech_synthesis_component)

        # Calling the main component
        asyncio.run(main_component(prev_result=None))
        main_component.print_resource_strategy()

        #########
        main_component = MainComponent(
            name=ComponentName.MAIN,
            call_model_name=None,
            resource_manager=resource_manager,
        )

        main_component.add_sub_component(ocr_component)
        ocr_component.add_sub_component(string_tools_component)
        string_tools_component.add_sub_component(llm_component)
        llm_component.add_sub_component(speech_synthesis_component)

        # Calling the main component
        asyncio.run(main_component(prev_result=None))
        main_component.print_resource_strategy()


if __name__ == "__main__":

    unittest.main()
