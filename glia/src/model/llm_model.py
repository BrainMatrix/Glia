from .base_model import BaseModel


from PIL import Image


class LLMModel(BaseModel):
    def __init__(self, tesseract_cmd=None):
        # init_model
        self.name = "llm"
        pass

    def __call__(self, data):
       
        text = (
            data + ",我是llm返回的结果"
            if data is not None
            else "None" + ",我是llm返回的结果"
        )
        return text
