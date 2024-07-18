import asyncio
from concurrent.futures import ThreadPoolExecutor


async def my_workflow_1(param):
    await asyncio.sleep(1)
    return f"Workflow 1 completed with param {param}"


async def my_workflow_2(param):
    await asyncio.sleep(2)
    return f"Workflow 2 completed with param {param}"


async def my_workflow_3(param):
    await asyncio.sleep(3)
    return f"Workflow 3 completed with param {param}"


def run_asyncio_in_thread(event_loop, coro, *args):
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(coro(*args))


def main():
    workflows = [
        (my_workflow_1, "hello"),
        (my_workflow_2, "world"),
        (my_workflow_3, "asyncio"),
    ]

    loops = [asyncio.new_event_loop() for _ in workflows]
    with ThreadPoolExecutor(max_workers=len(workflows)) as executor:
        futures = [
            executor.submit(run_asyncio_in_thread, loop, workflow, param)
            for (workflow, param), loop in zip(workflows, loops)
        ]

        # 获取所有workflow的结果
        for future in futures:
            print(future.result())  # 这里我们只是等待所有future完成

    # 关闭所有事件循环
    for loop in loops:
        loop.close()


if __name__ == "__main__":
    main()
