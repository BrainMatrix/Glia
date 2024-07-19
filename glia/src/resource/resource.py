# Copyright (c) BrainMatrix. All rights reserved.
class Resource(object):
    """A class that describes the composition of resources, including CPU, GPU, and multi-GPU.    
    :param use_cpu: Whether to use CPU resources, defaults to `False`
    :type use_cpu: boolean
    :param use_gpu: Whether to use GPU resources, defaults to `False`
    :type use_gpu: boolean
    :param use_multi_gpu_ids: List of GPU IDs to use in multi-GPU setup, defaults to None
    :type use_multi_gpu_ids: list
     
    """ 
    def __init__(self, use_cpu=False, use_gpu=False, use_multi_gpu_ids=[]):
        """Constructor method
        """
        self.use_cpu = use_cpu
        self.use_gpu = use_gpu
        self.use_multi_gpu_ids = use_multi_gpu_ids

    def __str__(self):
        """Return a string representation of a `Resource` object.        
        :return: String Representation of the Resource Object
        :rtype: str
        """
        return f"Resource(use_cpu={self.use_cpu}, use_gpu={self.use_gpu}, use_multi_gpu_ids={self.use_multi_gpu_ids})"

        # assert self.use_cpu or self.use_gpu, "At least one of CPU or GPU should be used"
        # assert (
        #     self.use_gpu and self.use_cpu
        # ), "Only CPU or GPU can be selected, not both"
