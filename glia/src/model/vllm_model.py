from .base_model import BaseModel
import requests
from PIL import Image
from config import rpc_url, api_key
from openai import OpenAI


class VLLMModel(BaseModel):
    """VLLM Model Class
    
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        #self.provider = "openai"
        self.model_name = "gpt-4o"#这个东西，应该是不同的model类对应一个名字，还是统一一个LLM类，然后利用这三个属性来实例化不同的llm模型
        self.client = OpenAI(
       # api_key=
        )
        """Constructor method
        
        """
        # init_model
        self.name = "VLLMModel"#这个属性似乎没啥用
        pass

    def __call__(self, content:dict[str, any], *args, **kwargs):
     
       resp = self.client.chat.completions.create(**content)
       
       return resp