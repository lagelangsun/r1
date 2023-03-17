import sys
import time


def read_util_ok():
    while input() != "OK":
        pass

def read_util_ok1():
    str_list = []
    str1 = ' '
    while str1 != 'OK':
        str1 = input()
        str_list.append(str1)
    return str_list
    
def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


if __name__ == '__main__':
    read_util_ok()
    finish()
    sys.stderr.write('111')
    while True:
        sttr = read_util_ok1()
        frame_id = int(sttr[0].strip("\n").split()[0])

        sys.stderr.write(str(frame_id))
        sys.stdout.write('%d\n' % frame_id)
        line_speed, angle_speed = 3, 1.5
        for robot_id in range(4):
            sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
            sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        finish()
