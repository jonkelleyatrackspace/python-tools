# Test in threading

def foo(bar, result, index):
    import random
    blockedfor=0.0000001#random.randint(1,5)
    import time; time.sleep(blockedfor)

#    res = 'blockedfor={2} index={1} hello {0}'.format(bar,index,blockedfor)
    randr = int(str(random.random())[-12:])
    res = { 'keys' : index , 'xx' : randr }
    result[index] = res

from threading import Thread

threads = [None] * 100
results = [None] * 100

for i in range(len(threads)):
    threads[i] = Thread(target=foo, args=('world!', results, i))
    threads[i].start()

# do some other stuff

for i in range(len(threads)):
    threads[i].join()
print results
print (" ".join(results))  # what sound does a metasyntactic locomotive make?
