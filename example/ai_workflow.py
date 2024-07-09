import asyncio

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from src.component.component_name import ComponentName
from src.component.llm_component import LLMComponent
from src.component.speech_recognition_component import SpeechRecognitionComponent
from src.component.string_tools_component import StringToolsComponent
from src.component.speech_synthesis_component import SpeechSynthesisComponent
from src.resource.resource import Resource
from src.resource.resource_manager import ResourceManager
from src.model.model_name import ModelName
from src.workflow.base_workflow import BaseWorkflow


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

    bwf = BaseWorkflow(
        workflow_name="Test_Workflow ID---1",
        components=[
            SpeechRecognitionComponent(
                name=ComponentName.SPEECH_RECOGNITION,
                call_model_name=ModelName.Whisper,
            ),
            StringToolsComponent(
                name=ComponentName.STRING_TOOLS,
                call_model_name=None,
            ),
            LLMComponent(
                name=ComponentName.LLM,
                call_model_name=ModelName.OPENCHAT,
            ),
            SpeechSynthesisComponent(
                name=ComponentName.TEXT_TO_SPEECH,
                call_model_name=ModelName.CHATTTS,
            ),
        ],
        resource_manager=resource_manager,
    )

    asyncio.run(bwf(data="这是用户输入的东西"))
    bwf.head_component.print_resource_strategy()
