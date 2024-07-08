# Copyright (c) BrainMatrix. All rights reserved.
class Resource:

    def __init__(self, use_cpu=False, use_gpu=False, use_multi_gpu_ids=[]):
        self.use_cpu = use_cpu
        self.use_gpu = use_gpu
        self.use_multi_gpu_ids = use_multi_gpu_ids

        # assert self.use_cpu or self.use_gpu, "At least one of CPU or GPU should be used"
        # assert (
        #     self.use_gpu and self.use_cpu
        # ), "Only CPU or GPU can be selected, not both"
