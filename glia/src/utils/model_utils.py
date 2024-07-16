import importlib

def get_model_instance(model_name: str):
    model_path_list = model_name.split(".")
    module_path = ".".join(model_path_list[:-1])
    class_name = model_path_list[-1]
    module = importlib.import_module(module_path)
    Instance = getattr(module, class_name)
    return Instance()
