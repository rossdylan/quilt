
import time
import zmq
from Queue import Queue

from nose.tools import eq_

import quilt

SLEEPY_TIME = 0.1  # in seconds
PAYLOAD = ["oh", "my word"]


class TestIncoming(object):
    def setUp(self):
        self.port = 13001
        self.queue = Queue()
        self.thread = quilt.IncomingThread(self.port, self.queue)
        self.sender = self.thread.context.socket(zmq.REQ)
        self.sender.connect("tcp://127.0.0.1:{0}".format(self.port))

    def test_initially_empty(self):
        assert self.thread.proc_queue.empty()

    def test_exit_right_away(self):
        self.thread.exit = True
        self.thread.start()
        self.thread.join()

    def test_stores_message_in_queue(self):
        self.thread.start()
        time.sleep(SLEEPY_TIME)
        self.thread.exit = True
        self.sender.send_multipart(PAYLOAD)
        ack = self.sender.recv_multipart()
        eq_(self.thread.proc_queue.get(), PAYLOAD)

    def has_one_got_one(self):
        self.thread.start()
        time.sleep(SLEEPY_TIME)
        self.thread.exit = True
        self.sender.send_multipart(PAYLOAD)
        ack = self.sender.recv_multipart()
        eq_(self.thread.proc_queue.qsize(), 1)

    def test_integration(self):
        # This tests more than one thing at once so its not really a unit test.

        assert self.thread.proc_queue.empty()
        self.thread.start()
        time.sleep(SLEEPY_TIME)

        self.sender.send_multipart(PAYLOAD)
        wat = self.sender.recv_multipart()
        assert not self.thread.proc_queue.empty()
        eq_(wat, ["ack"])

        self.thread.exit = True
        time.sleep(SLEEPY_TIME)

        self.sender.send_multipart(PAYLOAD)
        wat = self.sender.recv_multipart()
        eq_(wat, ["ack"])

        self.thread.join()

        eq_(self.thread.proc_queue.qsize(), 2)
