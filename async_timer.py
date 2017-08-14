from Queue import PriorityQueue
import time

class AsyncTimerEvent():
    def __init__(self, delay, repeat=False, callback=None, **kwargs):
        self.delay = delay
        self.timeout = time.time() + delay
        self.repeat = repeat
        self.callback = callback
        self.kwargs = kwargs

    def __cmp__(self, other):
        return cmp(self.timeout, other.timeout)

    def process(self):
        if self.callback:
            self.callback(**(self.kwargs))


class AsyncTimerQueue(PriorityQueue):
    def __init__(self, queue_name):
        PriorityQueue.__init__(self)
        self.queue_name = queue_name

    def timer_put(self, async_timer):
        assert isinstance(async_timer, AsyncTimerEvent)
        self.put(async_timer)

    def timer_get(self):
        return self.get()

    def timer_clean(self):
        self.queue = []

    # check if there is any timeout (no action taken)
    def timer_expired(self):

        if not self.empty():
            # peek smallest timeout event
            tmr_top = self.timer_get()
            timeout = tmr_top.timeout
            self.timer_put(tmr_top)
            return (time.time() >= timeout)
        else:
            return False

    # process all timeout events by now
    def timer_batch_process(self):
        timer_process_cnt = 0
        cur_time = time.time()
        while not self.empty():
            timer_top = self.timer_get()
            if cur_time >= timer_top.timeout:
                timer_top.process()
                timer_process_cnt += 1
                # for repeating timer events
                if timer_top.repeat:
                    timer_top.timeout = cur_time + timer_top.delay
                    self.timer_put(timer_top)
            else:
                self.timer_put(timer_top)
                break
        return timer_process_cnt
                
            

# ============================= for testing ================================
if __name__ == '__main__':
    def print_cb(**kwargs):
        for arg in kwargs.iteritems():
            print arg, time.time()

    q = AsyncTimerQueue("test_queue")
    q.timer_put(AsyncTimerEvent(5, True, print_cb))
    q.timer_put(AsyncTimerEvent(1.5, False, print_cb, **{"bb":22}))
    q.timer_put(AsyncTimerEvent(3, False, print_cb, **{"bb":22}))
    time.sleep(0.5)
    q.timer_put(AsyncTimerEvent(1, False, print_cb, **{"cc":222}))

    cnt = 0;
    while not q.empty():
        tmr_cnt = q.timer_batch_process()
        if tmr_cnt > 0:
            print 'timeout processed ', tmr_cnt
        else:
            cnt += 1
            if cnt > 20:
                q.timer_clean()
            time.sleep(0.5)
            print 'no timeout at', time.time()
