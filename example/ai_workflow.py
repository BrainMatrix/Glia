import asyncio

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


from glia.src.workflow.workflow_name import WorkflowName
from glia.src.workflow.llm_workflow import LLMWorkflow
from glia.src.workflow.speech_recognition_workflow import SpeechRecognitionWorkflow
from glia.src.workflow.string_tools_workflow import StringToolsWorkflow
from glia.src.workflow.speech_synthesis_workflow import SpeechSynthesisWorkflow
from glia.src.resource.resource import Resource
from glia.src.resource.resource_manager import ResourceManager
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.model.model_registry import ModelName
from glia.src.workflow.base_workflow import BaseWorkflow
from glia.src.workflow.main_workflow import MainWorkflow


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
    bwf = MainWorkflow(
        workflow_name="Test_Workflow ID---1",
        workflows=[
            SpeechRecognitionWorkflow(
                name=WorkflowName.SPEECH_RECOGNITION,
                call_model_name=ModelName.Whisper,
            ),
            StringToolsWorkflow(
                name=WorkflowName.STRING_TOOLS,
                call_model_name=None,
            ),
            LLMWorkflow(
                name=WorkflowName.LLM,
                call_model_name=ModelName.OPENCHAT,
            ),
            SpeechSynthesisWorkflow(
                name=WorkflowName.TEXT_TO_SPEECH,
                call_model_name=ModelName.CHATTTS,
            ),
        ],
        resource_manager=resource_manager,
    )
    input = "测试输入"
    output = asyncio.run(bwf(data=input))
    print(output)
    print(bwf.workflows[-1].process_result)
