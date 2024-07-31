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

from glia.src.schedule import Schedule
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
        loop=asyncio.get_event_loop(),
    ):
        """Constructor method"""
        super().__init__(
            name=name,
            resource_manager=resource_manager,
        )
        self.resource_manager = resource_manager
        self.loop = loop

        self.llm_agent_workflow = LLMWorkflow(
            name=WorkflowName.LLM,
            resource_manager=self.resource_manager,
            loop=self.loop,
        )
        self.sr_workflow = SpeechRecognitionWorkflow(
            name=WorkflowName.SPEECH_RECOGNITION,
            resource_manager=self.resource_manager,
            loop=self.loop,
        )
        self.tts_workflow = SpeechSynthesisWorkflow(
            name=WorkflowName.TEXT_TO_SPEECH,
            resource_manager=self.resource_manager,
            loop=self.loop,
        )
        self.schedule = schedule
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
        self.run(self.prev_result)

        return self.process_result

    def run(self, input):
        """Utilize user input to fully run the complete workflow of speech recognition -> LLM -> speech synthesis, and record the computation results.

        :param input: Input
        :type input: Any

        """
        # while not self.schedule.control_event.is_set():
        preprocessed_str = self.sr_workflow(input)
        llm_output = self.llm_agent_workflow(preprocessed_str)
        tts_output = self.tts_workflow(llm_output)

        self.process_result = tts_output


def run_asyncio_in_thread(loop, workflow, *args):

    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(workflow(*args))
    finally:
        loop.stop()
    return result


from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import nest_asyncio

nest_asyncio.apply()
app = FastAPI()


@app.get("/items/")
async def read_item(input: str):

    res = await my_workflow(input)
    print(my_workflow.print_resource_strategy())  # 目前实现的效果还是同步的

    return {"res": res}


if __name__ == "__main__":

    resource_manager = ResourceManager()

    resource_manager.register_model_list(
        {
            "Whisper": Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
            "Parseq": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0]),
            "OPENCHAT": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[1, 2]),
            "CHATTTS": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[3, 4]),
        }
    )

    schedule = Schedule()

    loop = asyncio.new_event_loop()
    my_workflow = TestAIWorkflow(
        name=WorkflowName.MAIN,
        resource_manager=resource_manager,
        schedule=schedule,
        loop=loop,
    )

    uvicorn.run(app, host="127.0.0.1", port=65501)
