import logging
from typing import Dict, List
from enum import Enum

from glia.src.resource import Resource

from glia.src.model import ModelName


# 定义资源管理类
class ResourceManager:
    def __init__(self):
        self.models: Dict[str, Resource] = {}  # 存储模型资源需求
        self.allocated_resources: Dict[str, Resource] = {}  # 存储已分配的资源
        self.monitored_models: List[str] = []  # 存储需要监控的模型

    def register_model(self, model_name: str, resources: Resource):
        self.models[model_name] = resources
        logging.info(f"Register model {model_name} with resources {resources}")

    def register_model_list(self, union_model_resources):
        for model_name, resources in union_model_resources.items():
            self.register_model(model_name, resources)
            # self.allocate_resources(model_name)
            logging.info(f"Register model {model_name} with resources {resources}")

    def allocate_resources(self, model_name: str):
        if model_name in self.models:
            self.allocated_resources[model_name] = self.models[model_name]
            logging.info(
                f"Allocated resources for model {model_name}: {self.models[model_name]}"
            )
        else:
            logging.warning(f"Model {model_name} not found")

    def monitor_model(self, model_name: str):
        if model_name in self.models:
            self.monitored_models.append(model_name)
            logging.info(f"Monitoring started for model {model_name}")
        else:
            logging.warning(f"Model {model_name} not found")

    def adjust_resources(self, model_name: str, new_resources: Resource):
        if model_name in self.allocated_resources:
            self.allocated_resources[model_name] = new_resources
            logging.info(
                f"Adjusted resources for model {model_name} to {new_resources}"
            )
        else:
            logging.warning(f"Model {model_name} not found or not allocated")

    def set_security_policy(self, model_name: str, policy: str):
        logging.info(f"Set security policy for model {model_name}: {policy}")

    def set_permissions(self, model_name: str, permissions: List[str]):
        logging.info(f"Set permissions for model {model_name}: {permissions}")

    def log_resources(self):
        logging.info(f"Currently allocated resources: {self.allocated_resources}")


# 示例使用
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # # 创建资源管理器实例
    # resource_manager = ResourceManager()

    # # 定义模型资源需求
    # model_resources = Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[])

    # # 添加模型及其资源需求
    # resource_manager.register_model("Model_A", model_resources)

    # print("test", resource_manager.models["Model_A"])

    # # 为模型分配资源
    # resource_manager.allocate_resources("Model_A")

    # # 监控模型
    # resource_manager.monitor_model("Model_A")

    # # 调整模型资源
    # new_resources = Resource(use_cpu=True, use_gpu=True, use_multi_gpu_ids=[])
    # resource_manager.adjust_resources("Model_A", new_resources)

    # # 设置安全策略
    # resource_manager.set_security_policy("Model_A", "SSL/TLS encryption")

    # # 设置权限
    # resource_manager.set_permissions("Model_A", ["user1", "user2"])

    # # 记录当前资源状态
    # resource_manager.log_resources()
    from glia.src.model import ModelName

    resource_manager = ResourceManager()

    resource_manager.register_model(
        ModelName.Whisper.value,
        Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
    )

    resource_manager.register_model(
        ModelName.Parseq.value,
        Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
    )

    resource_manager.register_model(
        ModelName.OPENCHAT.value,
        Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
    )

    resource_manager.register_model(
        ModelName.CHATTTS.value,
        Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[]),
    )
    a = ModelName.CHATTTS
    print(type(a))
    print("test", resource_manager.models[a.value])
