
import time
import zmq
from Queue import Queue

from nose.tools import eq_

import quilt

class TestIncoming(object):
    def setUp(self):
        self.port = 13001
        self.queue = Queue()
        self.thread = quilt.IncomingThread(self.port, self.queue)
        self.sender = self.thread.context.socket(zmq.REQ)
        self.sender.connect("tcp://127.0.0.1:{0}".format(self.port))

    def testStartStop(self):
        # TODO -- this tests more than one thing at once.  It should be
        # decomposed into more smaller tests.

        assert self.thread.proc_queue.empty()
        self.thread.start()
        time.sleep(1)

        self.sender.send_multipart(["oh", "my god"])
        wat = self.sender.recv_multipart()
        assert not self.thread.proc_queue.empty()
        eq_(wat, ["ack"])

        self.thread.exit = True
        time.sleep(1)

        self.sender.send_multipart(["oh", "my god"])
        wat = self.sender.recv_multipart()
        eq_(wat, ["ack"])

        self.thread.join()

        eq_(self.thread.proc_queue.qsize(), 2)
