from .base_model import BaseModel
import requests
from PIL import Image
from config import rpc_url, api_key
from chromadb import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('/mnt/nfs_share_test/yangruiqing/langchain_demo/bge-small-zh-v1.5')

class SentenceTransformerModel(BaseModel, EmbeddingFunction):
    """SentenceTransformer Model Class
    
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        """Constructor method
        
        """
        # init_model
        self.name = "SentenceTransformerModel"
        pass

    def __call__(self, texts: Documents, *args, **kwargs) -> Embeddings:
        
       embeddings = [list(model.encode(text,normalize_embeddings=True).astype(float)) for text in texts]
       
       return embeddings