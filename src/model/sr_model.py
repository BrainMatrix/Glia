from .base_model import BaseModel

from PIL import Image


class SRModel(BaseModel):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        # init_model
        self.name = "SRModel"
        pass

    def __call__(self, data):
        text = (
            data + ",我是sr返回的结果"
            if data is not None
            else "None" + ",我是sr返回的结果"
        )
        return text
