import functools
import logging


class GlobalExceptionHandler:
    def __init__(self):
        # 配置日志记录
        logging.basicConfig(
            level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def handle_exceptions(self, func):
        """
        装饰器：捕获并处理函数中的所有异常。
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 在这里处理异常，例如记录日志
                logging.error(f"Exception occurred in function '{func.__name__}': {e}")
                # 可以选择重新抛出异常或者返回一个特定的值
                # raise
                return None

        return wrapper

exception_handler = GlobalExceptionHandler()

# if __name__ == '__main__':
#     # 使用示例
#     exception_handler = GlobalExceptionHandler()


#     @exception_handler.handle_exceptions
#     def divide(x, y):
#         return x / y


#     @exception_handler.handle_exceptions
#     def cause_error():
#         raise ValueError("An error occurred!")


#     # 调用函数
#     print(divide(10, 2))  # 正常执行
#     print(divide(10, 0))  # 将捕获并记录除以零的异常
#     print(cause_error())  # 将捕获并记录ValueError
