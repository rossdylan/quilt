import quilt
import random
import time

class TestProtocol(object):

    def setUp(self):
        self.serverOne = quilt.QuiltServer("localhost", random.randint(4000, 20000))
        self.serverTwo = quilt.QuiltServer("127.0.0.1", random.randint(4000, 20000)+1)

        self.serverOne.start()
        self.serverTwo.start()
        self.serverOne.protocol.connect_to_server('127.0.0.1',
            self.serverTwo.incoming_port)

    def test_server_connect_outgoing(self):
        assert self.serverTwo.addr in self.serverOne.protocol.outgoing_queues

    def test_server_connect_incoming(self):
        time.sleep(2)
        print self.serverOne.addr
        print self.serverTwo.protocol.outgoing_queues
        assert self.serverOne.addr in self.serverTwo.protocol.outgoing_queues
