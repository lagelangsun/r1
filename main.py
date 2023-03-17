import sys
import time


def read_util_ok():
    while input() != "OK":
        pass

def read_util_ok1():
    str_list = []
    while str != 'OK':
        str = input()
        sys.stderr.write(str)
        sys.stderr.write("\n")
        str_list.append(str)
    return str_list
    
def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


if __name__ == '__main__':
    read_util_ok()
    finish()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.split(' ')
O        frame_id = int(parts[0])
        # time.sleep(0.05)
        read_util_ok()
        sys.stderr.write(frame_id)

        sys.stdout.write('%d\n' % frame_id)
        line_speed, angle_speed = 3, 1.5
        for robot_id in range(4):
            sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
            sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        finish()
