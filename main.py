import sys
import numpy as np
import time
from A_IO_demo3_3 import IOProcess
# content = sys.stdin.readline()
# print(content)

def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


def read_util_ok():         # 该函数用于读取输入直到得到一个OK
    while input() != "OK": pass
    
if __name__ == '__main__':
    io_model = IOProcess()
    io_model.getInfoFromServer()