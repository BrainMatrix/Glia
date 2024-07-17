from typing import List, Dict, Any
import importlib
import logging
from enum import Enum

from glia.src.workflow import WorkflowName
from glia.src.workflow import BaseWorkflow
from glia.src.workflow import LLMWorkflow
from glia.src.workflow import SpeechRecognitionWorkflow
from glia.src.workflow import SpeechSynthesisWorkflow
from glia.src.model.model_name import ModelName
from glia.src.resource.resource import Resource
from glia.src.resource.resource_manager import ResourceManager


import asyncio


class my_ai_algorithm(BaseWorkflow):
    """

    Some Fancy AI algorithm. We get an input image and a question, output some result.

    """

    def __init__(
        self,
        name: Enum = None,
        call_model_name: Enum = None,
        resource_manager: ResourceManager = None,
        prev_result: Any = None,
    ):

        super().__init__(name, call_model_name, resource_manager, prev_result)
        self.resource_manager = resource_manager
        self.llm_agent_workflow = LLMWorkflow(
            name=WorkflowName.LLM,
            resource_manager=self.resource_manager,
        )
        self.sr_workflow = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,
            resource_manager=self.resource_manager,
        )
        self.tts_workflow = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            resource_manager=self.resource_manager,
        )
        self.add_sub_workflow(
            self.sr_workflow, self.llm_agent_workflow, self.tts_workflow
        )

    async def __call__(self, input):
        self.prev_result =  input
        await self.run(self.prev_result)

        return self.process_result

    async def run(self, input):
        preprocessed_str = await self.sr_workflow(input)
        llm_output = await self.llm_agent_workflow(preprocessed_str)
        tts_output = await self.tts_workflow(llm_output)

        self.process_result = tts_output


if __name__ == "__main__":

    resource_manager = ResourceManager()

    resource_manager.register_model_list(
        {
            ModelName.Whisper: Resource(
                use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]
            ),
            ModelName.Parseq: Resource(
                use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0]
            ),
            ModelName.OPENCHAT: Resource(
                use_cpu=False, use_gpu=True, use_multi_gpu_ids=[1, 2]
            ),
            ModelName.CHATTTS: Resource(
                use_cpu=False, use_gpu=True, use_multi_gpu_ids=[3, 4]
            ),
        }
    )
    my_workflow = my_ai_algorithm(
        name=WorkflowName.MAIN, resource_manager=resource_manager
    )

    output = asyncio.run(my_workflow("hello"))
    print("final result: ", output)

    my_workflow.print_resource_strategy()
