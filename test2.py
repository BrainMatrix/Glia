import asyncio


async def bwf(data):
    # 假设这个函数处理一些异步操作
    return 222


# 使用 asyncio.run 来执行 bwf 协程并获取结果
result = asyncio.run(bwf(data="这是用户输入的东西"))
print(result)
