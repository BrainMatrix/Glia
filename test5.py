import asyncio
import random
import threading
from concurrent.futures import ThreadPoolExecutor


# 假设这是获取传感器数据的异步函数
async def get_sensor_data():
    await asyncio.sleep(0.1)  # 模拟异步操作
    return random.uniform(0, 1)


# 异步摔倒处理逻辑
async def handle_fall():
    print("处理摔倒逻辑...")
    await asyncio.sleep(5)  # 模拟异步处理过程
    print("摔倒逻辑处理完毕")


# 异步监控摔倒的函数
async def monitor_fall(stop_event):
    while not stop_event.is_set():
        data = await get_sensor_data()
        if data < 0.8:
            print("警报：老人摔倒了！")
            stop_event.set()  # 设置事件，通知其他线程停止
            await handle_fall()  # 处理摔倒逻辑
            stop_event.clear()  # 清除事件，允许其他线程继续
            return 
        await asyncio.sleep(1)


# 异步workflow函数
async def my_workflow(arg, stop_event):
    print(f"Workflow started with argument: {arg}")
    try:
        while not stop_event.is_set():  # 检查是否需要停止
            await asyncio.sleep(0.5)  # 模拟异步操作
            print("Workflow running...")
    except asyncio.CancelledError:
        print("Workflow stopped due to fall alert")
    return f"Workflow result with argument: {arg}"


# 在线程中运行异步函数
def run_asyncio_in_thread(loop, coro, *args):
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro(*args))


# 创建一个事件对象
stop_event = asyncio.Event()

# 创建并启动监控摔倒的线程
monitor_loop = asyncio.new_event_loop()
monitor_thread = threading.Thread(
    target=run_asyncio_in_thread, args=(monitor_loop, monitor_fall, stop_event)
)
monitor_thread.start()

# 创建并启动执行workflow的线程
workflow_loop = asyncio.new_event_loop()
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(
        run_asyncio_in_thread, workflow_loop, my_workflow, "hello", stop_event
    )
    output = future.result()  # 获取workflow的结果

# 等待监控摔倒的线程结束
monitor_thread.join()

print(f"Workflow output: {output}")
