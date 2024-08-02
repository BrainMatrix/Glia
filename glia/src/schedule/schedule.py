import heapq
import threading
import time
import queue
import pika


class DynamicPriorityQueue(queue.PriorityQueue):
    """在queue的基础上增加查看队首元素的接口
    """
        
    def check_head_element(self):
         with self.mutex:
            if not self.queue:
                #raise queue.Empty
                return None
            # 返回队首元素
            return self.queue[0]


class Schedule:
    """Priority class
    """
    def __init__(self):     
        #队列的创建需要动态创建，待改进
        self.llm_service_queue = DynamicPriorityQueue(maxsize=0)
        self.ocr_service_queue = DynamicPriorityQueue(maxsize=0)
        self.speech_recognition_service_queue = DynamicPriorityQueue(maxsize=0)
        self.speech_synthesis_service_queue = DynamicPriorityQueue(maxsize=0)
        self.emergency_service_queue = DynamicPriorityQueue(maxsize=0)#紧急事件队列
        
        
    

        
    


            
    
