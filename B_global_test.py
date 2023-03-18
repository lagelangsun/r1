a = 2
 
class GlobalTest(object):
    def __init__(self):
        self.a = 0
        
    def f(self,a):
        print(a)

    def change(self):
        global a 
        a = 10

    def main(self):
        global a
        a += 1
        self.f(a)
 
if __name__ == '__main__':
    global_test = GlobalTest()
    print(a)
    global_test.main()
    global_test.change()
    print(a)