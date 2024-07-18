import heapq
import threading
import time
import queue


class Task:
    def __init__(self, description, total_steps=1):
        self.description = description
        self.total_steps = total_steps
        self.current_step = 0  # 从0开始，标识当前执行到第几步

    def execute_step(self):
        if self.current_step < self.total_steps:
            self.current_step += 1  # 执行当前步骤并递增
            time.sleep(1)  # 模拟执行时间
            print(
                f"执行 {self.description} 的步骤 {self.current_step}/{self.total_steps}"
            )
            if self.current_step == self.total_steps:
                return True  # 表示任务完成
        return False  # 任务未完成

    def __str__(self):
        return self.description


class DynamicPriorityQueue:
    def __init__(self):
        self.lock = threading.Lock()
        self.pq = []
        self.counter = 0

    def put(self, priority, task):
        with self.lock:
            heapq.heappush(self.pq, (priority, self.counter, task))
            self.counter += 1

    def get(self):
        with self.lock:
            if self.pq:
                return heapq.heappop(self.pq)[2]
            raise queue.Empty

    def empty(self):
        with self.lock:
            return not self.pq


class Schedule:
    def __init__(self):
        self.pq = DynamicPriorityQueue()
        self.control_event = threading.Event()
        self.workers = []

    def add_task(self, priority, task):
        self.pq.put(priority, task)

    def start(self, num_workers=1):
        for _ in range(num_workers):
            worker = threading.Thread(target=self.worker_task)
            self.workers.append(worker)
            worker.start()

    def worker_task(self):
        while not self.pq.empty():
            try:
                task = self.pq.get()
                print(f"开始执行任务: {task}")

                while not task.execute_step():  # 循环执行任务直到完成
                    if (
                        task.description == "Urgent task"
                        and not self.control_event.is_set()
                    ):
                        print(f"任务 {task} 暂停，插入新任务并重新调度")
                        self.pq.put(
                            1, Task("优先级1的任务", 3)
                        )  # 假设优先级1的任务需要3个步骤
                        self.control_event.set()
                        self.pq.put(4, task)  # 重新插入当前任务到队列中
                        break

                if task.current_step == task.total_steps:
                    print(f"任务 {task} 完成")
            except queue.Empty:
                break

    def join(self):
        for worker in self.workers:
            worker.join()


if __name__ == "__main__":
    # 使用 Schedule 类
    schedule = Schedule()

    tasks = [
        (2, Task("优先级2的任务", 2)),
        (3, Task("优先级3的任务", 3)),
        (4, Task("优先级4的任务", 4)),
        (6, Task("优先级6的任务", 2)),
        (5, Task("优先级5的任务", 3)),
        (5, Task("Urgent task", 3)),
    ]

    for priority, task in tasks:
        schedule.add_task(priority, task)

    schedule.start(num_workers=1)  # 启动两个工作线程
    schedule.join()  # 等待所有工作线程完成

    print("所有任务已完成。")
