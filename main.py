import logging

TIMEOUT_KEEP_ALIVE = 10  # seconds

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ],
                    )

import json
import fastapi
import openai_api_protocol
import argparse
import uvicorn
import time

from fastapi import BackgroundTasks, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from dataclasses import dataclass

from typing import AsyncGenerator, Optional
from vllm.outputs import RequestOutput
from vllm.utils import random_uuid
from vllm.engine.arg_utils import AsyncEngineArgs

from config import rpc_url, api_key
from glia.src.workflow.RPBot_flow import RPBot_Workflow
from glia.src.workflow import WorkflowName
from glia.src.resource.resource_manager import ResourceManager
from glia.src.resource.resource import Resource
from glia.src.schedule.schedule import Schedule
from glia.src.workflow.vllm_workflow import VLLMWorkflow

@dataclass
class ModelConfig:
    names: set = None

    max_length: int = None
    stream_period: int = None
    eot_tokens: list = None

    enable_sys_prompt: bool = None
    api_keys: list = None

resource_manager = ResourceManager()

resource_manager.register_model_list(
        {   "Whisper": Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
            "Parseq": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0]),
            "OPENCHAT": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[1, 2]),
            "CHATTTS": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[3, 4]),
            "VLLM": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[5, 6]),
            "SentenceTransformer": Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[7, 8]),
        }#这里的注册资源数量需要与schedule中的实例化的service数量保持一致
    )
    
schedule = Schedule(resource_manager=resource_manager)

bot = RPBot_Workflow(name=WorkflowName.VLLM, schedule=schedule, profile_path="/mnt/nfs_share_test_online/make/Glia/glia/json/lishen.json",url=rpc_url,api_key=api_key)

vllm_worflow = VLLMWorkflow(name=WorkflowName.VLLM,
                            service_priority=3,
                            schedule=schedule,
                            needs=[],
                            stream = True,
                            temperature = 0.9, 
                            url = bot.url,
                            api_key = bot.key,#这个属性由嵌套flow来设置
                            )
#add_sub_workflow的前提是，把vllm_workflow的属性都设置好，除了传入的message数据
bot.add_sub_workflow(vllm_worflow)

logger = None
app = fastapi.FastAPI()

model = ModelConfig()
tokenizer = None

def log_request(created_time: int, request: openai_api_protocol.ChatCompletionRequest, output: RequestOutput):
    if logger is not None:
        logger.info(openai_api_protocol.LoggingRecord(
            time=created_time,
            request=request,
            outputs=[o.text for o in output.outputs]
        ).model_dump_json(exclude_unset=True))

   
@app.get("/v1/models")
async def show_available_models():
    """Show available models. Right now we only have one model."""

    return openai_api_protocol.ModelList(data=[
        openai_api_protocol.ModelCard(id=name,
                                      root=name,
                                      permission=[openai_api_protocol.ModelPermission()])
    for name in model.names])        

last_user = None
@app.post("/v1/chat/completions")
async def fetch_data(raw_request: Request, background_tasks: BackgroundTasks):
    logging.info("start: =================================")
    request = openai_api_protocol.ChatCompletionRequest(**await raw_request.json())
    logging.info(request)

    global last_user
    if last_user != request.user:
        bot.init_memory(request.user) # 第一次加载
        last_user = request.user

    print("request.messages",request.messages)
    
  
    full_resp = bot(request.messages)
    request_id =  f"cmpl-{random_uuid()}"
    created_time = int(time.time())
    model_name = request.model

    def create_stream_response_json(
        index: int,
        text: str,
        finish_reason: Optional[str] = None,
    ) -> str:
        choice_data = openai_api_protocol.ChatCompletionResponseStreamChoice(
            index=index,
            delta=openai_api_protocol.DeltaMessage(content=text),
            finish_reason=finish_reason,
        )
        response = openai_api_protocol.ChatCompletionStreamResponse(
            id=request_id,
            choices=[choice_data],
            model=model_name,
        )

        return response.model_dump_json(exclude_unset=True)
    

    async def completion_stream_generator() -> AsyncGenerator[str, None]:
        for i in range(request.n):
            choice_data = openai_api_protocol.ChatCompletionResponseStreamChoice(
                index=i,
                delta=openai_api_protocol.DeltaMessage(role="assistant"),
                finish_reason=None,
            )
            chunk = openai_api_protocol.ChatCompletionStreamResponse(id=request_id,
                                                                    choices=[choice_data],
                                                                    model=model_name)
            yield f"data: {chunk.model_dump_json(exclude_unset=True)}\n\n"
        final_res = None
        delta_text_list = []    

        for index,chunk  in enumerate(full_resp):
            print(chunk)
            final_res = chunk
            index = 0
            delta_text = chunk.choices[0].delta.content
            if delta_text is not None:
               delta_text_list.append(delta_text)
               yield f"data: {create_stream_response_json(index=index, text=delta_text)}\n\n"
            yield f"data: {create_stream_response_json(index=index, text='', finish_reason=chunk.choices[0].finish_reason)}\n\n"
        
        bot.update_memory("".join(delta_text_list))
        background_tasks.add_task(log_request, created_time, request, final_res)
        background_tasks.add_task(post_stream_tasks, request.user)

    response =  StreamingResponse(completion_stream_generator(),
                        media_type="text/event-stream") 
    return response

def post_stream_tasks(user_ud):
    # 这些是你希望在返回 StreamingResponse 之后执行的操作
    msg = f"同user{user_ud}本轮对话结束"
    logging.info(msg)




if __name__ == '__main__':


    parser = argparse.ArgumentParser(description="OpenChat OpenAI-Compatible RESTful API server.")

    # Model
    parser.add_argument("--model-type", type=str, default=None, help="Model type. Leave empty to auto-detect.")

    parser.add_argument("--stream-period", type=int, default=6, help="Number of tokens per stream event")
    parser.add_argument("--api-keys", type=str, nargs="*", default=[], help="Allowed API Keys. Leave blank to not verify")
    parser.add_argument("--enable-sys-prompt", default=False, action="store_true")

    # Server
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host name")
    parser.add_argument("--port", type=int, default=18886, help="Port number")
    parser.add_argument("--allow-credentials", action="store_true", help="Allow credentials")
    parser.add_argument("--allowed-origins", type=json.loads, default=["*"], help="Allowed origins")
    parser.add_argument("--allowed-methods", type=json.loads, default=["*"], help="Allowed methods")
    parser.add_argument("--allowed-headers", type=json.loads, default=["*"], help="Allowed headers")

    # Logging
    parser.add_argument("--log-file", type=str, default=None, help="Log file. Leave blank to disable logging")
    parser.add_argument("--log-max-mb", type=int, default=128, help="Max log size in MB")
    parser.add_argument("--log-max-count", type=int, default=10, help="Max log file versions to keep")
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()


    uvicorn.run(app,
                    host=args.host,
                    port=args.port,
                    log_level="info",
                    access_log=False,
                    timeout_keep_alive=TIMEOUT_KEEP_ALIVE)

