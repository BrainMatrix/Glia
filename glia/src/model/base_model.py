from abc import ABC, abstractmethod


class BaseModel(ABC):
    """This is a Model base class that defines two abstract methods, `__init__` and `__call__`, which need to be implemented in the subclasses.

    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.model_name = None
        pass
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass
        