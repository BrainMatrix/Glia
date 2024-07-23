from .base_model import BaseModel


from PIL import Image


class OCRModel(BaseModel):
    """OCR Model Class
    
    """
    def __init__(self,*args, **kwargs):
        """Constructor method
        
        """
        # init_model
        self.name = "ocr"
        pass

    def __call__(self, data):
    
        text = (
            data + ",我是ocr返回的结果"
            if data is not None
            else "None" + ",我是ocr返回的结果"
        )
        return text
