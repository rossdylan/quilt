import quilt
import random
import time

MESSAGE_PAYLOAD = "omgquiltfosslol"


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

    def test_send_message(self):
        time.sleep(2)
        self.serverOne.protocol.send_message("unit_test_user",
                "testing_channel",
                MESSAGE_PAYLOAD)

        server_two_msg = self.serverTwo.protocol.message_queue.get()
        server_three_msg = self.serverThree.protocol.message_queue.get()

        assert server_two_msg['message'] == MESSAGE_PAYLOAD
        assert server_three_msg['message'] == MESSAGE_PAYLOAD

        assert server_two_msg['user'] == "unit_test_user"
        assert server_three_msg['user'] == "unit_test_user"

        assert server_two_msg['channel'] == "testing_channel"
        assert server_three_msg['channel'] == "testing_channel"


    def tearDown(self):
        time.sleep(4)
        self.serverOne.terminate_threads()
        self.serverTwo.terminate_threads()
        self.serverThree.terminate_threads()
