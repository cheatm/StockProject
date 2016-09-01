import  threading
import time

def test():
    thread1=threading.Thread(target=t1)
    thread2=threading.Thread(target=t2)
    thread=[thread1,thread2]
    for t in thread:
        t.start()

    print('end')


def t1():
    print('t1')
    time.sleep(5)

def t2():
    print('t2')

if __name__ == '__main__':
    test()