import sys
import numpy as np
import time
import threading


# class ThreadTest(threading.Thread):
 
#     def __init__(self, time_1,  *args, **kwargs):
#         super(ThreadTest, self).__init__(*args, **kwargs)
#         self.time = time_1
#         self.thread1 = threading.Thread(target=self.printTest,args=1)
#         self.thread2 = threading.Thread(target=self.printTest,args=2)

#     def my_run(self):
#         self.thread1.start()
#         self.thread2.start()
#         self.thread1.join()
#         self.thread2.join()
        
#     def printTest(self, a):
#         print('thread',a,  'run num:')
#         time.sleep(2)
#         print('thread', a, 'run time', time.time()-self.time)

class ThreadTest(threading.Thread):
 
    def __init__(self, num, time_1, event , *args, **kwargs): 
        super(ThreadTest, self).__init__(*args, **kwargs)
        self.num = num
        self.time = time_1
        self.event = event
        print('thread', num, 'init')
 
    def run(self):
        event.wait()
        time.sleep(self.num)
        print('thread', self.num, 'run time', time.time()-self.time-2)

# class MyClass(object):
#     def __init__(self, time_1):
#         self.flag = True
#         self.time_1 = time_1
#         self.thread_test = [ThreadTest(0,time_1),ThreadTest(1,time_1),ThreadTest(2,time_1),ThreadTest(3,time_1)]
#         self.count = 0

#     def my_run(self):
#         while True:
#             self.count += 1
        

# class ThreadTest(threading.Thread):
 
#     def __init__(self, num, time_1,  *args, **kwargs): 
#         super(ThreadTest, self).__init__(*args, **kwargs)
#         self.num = num
#         self.time = time_1
#         print('thread', num, 'init')
 
#     def run(self):
#         while True:
#             if
#         time.sleep(self.num)
#         print('thread', self.num, 'run time', time.time()-self.time)
 
if __name__ == "__main__":

    # a = MyClass(time.time())

    # thread_test = ThreadTest(time.time()
    #                          )
    # thread_test.my_run()

    event = threading.Event()
    # while True:
    thread_list = []
    time_1 = time.time()
    for i in range(3):
        dt = ThreadTest(i,time_1,event)
        dt.start()
        thread_list.append(dt)
    time.sleep(2)
    event.set()
    
    for child_thread in thread_list:
        child_thread.join()
