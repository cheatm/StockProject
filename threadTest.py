import  threading,time
import threadpool





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
    return [1,2,3,4]

def t2(*args,**kwargs):

    return args

def callBack(req,out):
    kwds=req.kwds
    print(req.kwds['a'])
    origin[req.requestID]=out

if __name__ == '__main__':
    pool=threadpool.ThreadPool(5)
    global origin
    origin={}
    pool.putRequest(
        threadpool.WorkRequest(t2,[1,2,3],{'a':1},callback=callBack)
    )
    pool.putRequest(
        threadpool.WorkRequest(t2,[4,6,0],{'a':1},callback=callBack)
    )

    pool.wait()
    print(origin)

