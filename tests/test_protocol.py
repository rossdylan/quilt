import quilt
import random
import time

class TestProtocol(object):

    def setUp(self):
        self.serverOne = quilt.QuiltServer("localhost", random.randint(4000, 20000))
        self.serverTwo = quilt.QuiltServer("127.0.0.1", random.randint(4000, 20000)+1)
        self.serverThree = quilt.QuiltServer("127.0.0.1", random.randint(4000, 20000)+2)

        self.serverOne.start()
        self.serverTwo.start()
        self.serverThree.start()

        self.serverOne.protocol.connect_to_server('127.0.0.1',
            self.serverTwo.incoming_port)

        self.serverThree.protocol.connect_to_server('127.0.0.1',
            self.serverTwo.incoming_port)

    def test_server_connect_outgoing(self):
        assert self.serverTwo.name in self.serverOne.protocol.outgoing_queues
        assert self.serverTwo.name in self.serverThree.protocol.outgoing_queues

    def test_server_connect_incoming(self):
        time.sleep(1)
        print self.serverTwo.protocol.outgoing_queues
        assert self.serverOne.name in self.serverTwo.protocol.outgoing_queues
        assert self.serverThree.name in self.serverTwo.protocol.outgoing_queues

    def test_send_ping(self):
        time.sleep(2)
        print self.serverTwo.protocol.outgoing_queues
        self.serverOne.protocol.ping_server(self.serverTwo.name)
        time.sleep(2)
        print self.serverOne.protocol.last_pongs
        assert self.serverOne.protocol.last_pongs != {}

    def test_send_join(self):
        self.serverOne.protocol.send_join("unit_test_user", "testing_channel")
        time.sleep(2)
        assert "testing_channel" in self.serverTwo.protocol.channels
        assert "unit_test_user" in self.serverTwo.protocol.channels["testing_channel"].users

    def tearDown(self):
        self.serverOne.terminate_threads()
        self.serverTwo.terminate_threads()
        self.serverThree.terminate_threads()
