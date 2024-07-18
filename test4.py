import sched
import time
from datetime import datetime, timedelta

# 创建一个调度器实例
scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)


# 定义要执行的任务
def scheduled_task(name):
    print(f"Task {name} executed at {datetime.now()}")


# 定义一个函数来安排任务
def schedule_task(task_name, delay_seconds):
    # 计算任务执行的时间
    execution_time = datetime.now() + timedelta(seconds=delay_seconds)
    # 安排任务
    scheduler.enterabs(
        time.mktime(execution_time.timetuple()), 1, scheduled_task, (task_name,)
    )


# 安排几个示例任务
schedule_task("A", 10)  # 10秒后执行任务A
schedule_task("B", 20)  # 20秒后执行任务B
schedule_task("C", 30)  # 30秒后执行任务C

# 启动调度器
scheduler.run()
