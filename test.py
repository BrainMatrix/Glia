def decorator(func):
    def wrapper(*args, **kwargs):
        print("装饰器添加的功能")
        return func(*args, **kwargs)

    return wrapper


@decorator
def say_hello(name):
    print(f"Hello, {name}")


# 调用装饰过的函数
say_hello("World")  # 输出: 装饰器添加的功能 和 Hello, World


def call_decorator(callable_obj):
    def wrapper(*args, **kwargs):
        print("装饰器添加的功能")
        return callable_obj(*args, **kwargs)

    return wrapper


class CallableClass:
    def __call__(self, *args, **kwargs):
        print("实例被调用", args, kwargs)


# 使用装饰器装饰类的实例
instance = call_decorator(CallableClass())(1, 2, a=3, b=4)
# 输出: 装饰器添加的功能
# 输出: 实例被调用 (1, 2) {'a': 3, 'b': 4}


class CallableBase:
    def __call__(self, *args, **kwargs):
        print("CallableBase 被调用", args, kwargs)

class CallableDerived(CallableBase):
    # 这里没有定义 __call__ 方法，所以会继承 CallableBase 的 __call__ 方法
    pass

# 创建 CallableDerived 的实例
derived_instance = CallableDerived()

# 调用实例，会调用 CallableBase 的 __call__ 方法
derived_instance(1, 2, a=3, b=4)  # 输出: CallableBase 被调用 (1, 2) {'a': 3, 'b': 4}



class CallableDerived(CallableBase):
    def __call__(self, *args, **kwargs):
        print("CallableDerived 被调用", args, kwargs)


# 创建 CallableDerived 的实例
derived_instance = CallableDerived()

# 调用实例，会调用 CallableDerived 的 __call__ 方法
derived_instance(1, 2, a=3, b=4)  # 输出: CallableDerived 被调用 (1, 2) {'a': 3, 'b': 4}
