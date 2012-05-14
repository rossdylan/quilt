import zmq
from threading import Thread
from Queue import Queue, Empty
import time


class IncomingThread(Thread):
    """
    The Incoming thread handles connections from servers and passes the
    data they send off to the processors

    :type listen_port: int
    :param listen_port: the port to listen for connecting servers on

    :type proc_queue: Queue
    :param proc_queue: The queue to pass messages off to processor with
    """

    def __init__(self, listen_port, proc_queue):
        self.listen_port = listen_port
        self.proc_queue = proc_queue
        self.context = zmq.Context()
        self.incoming = self.context.socket(zmq.REP)
        self.exit = False
        super(IncomingThread, self).__init__()

    def run(self):
        try:
            return self._run()
        finally:
            self.incoming.close()

    def _run(self):
        self.incoming.bind("tcp://*:{0}".format(self.listen_port))
        while True:
            if self.exit:
                break
            data = self.incoming.recv_multipart()
            self.proc_queue.put(data)
            # TODO - probably should change this to something proper
            self.incoming.send("ack")


class ProcessorThread(Thread):
    """
    This thread takes data out of the proc_queue and
    does things to that data based on the protocol

    :type proc_queue: Queue
    :param proc_queue: Queue of data to be processed

    :type protocol: QuiltProtocol
    :param protocol: the object used to parse the data recieved
    """

    def __init__(self, proc_queue, protocol):
        super(ProcessorThread, self).__init__()
        self.proc_queue = proc_queue
        self.protocol = protocol

    def run(self):
        while True:
            try:
                data = self.proc_queue.get_nowait()
                if data == None:
                    break
                self.protocol.handle(*data)
            except Empty:
                time.sleep(1)


class OutgoingThread(Thread):
    """
    For each outgoing connection one of these threads is created
    and it will forward the data in its personal Queue to the destination

    :type addr: str
    :param addr: Address of the server to connect to

    :type port: int
    :param port: port number of the server to connect to

    :type queue: Queue
    :param queue: Data queue for outgoing data for this connection
    """

    def __init__(self, addr, port, queue):
        super(OutgoingThread, self).__init__()
        self.address = "tcp://{0}:{1}".format(addr, port)
        self.queue = queue
        self.context = zmq.Context()
        self.outgoing = self.context.socket(zmq.REQ)

    def run(self):
        self.outgoing.connect(self.address)
        while True:
            data = self.queue.get()
            if data == None:
                break
            data = [str(i) for i in data]
            self.outgoing.send_multipart(data)
            self.outgoing.recv()  # Get our ACK


class QuiltServer(object):
    """
    The main server class for Quilt, spins up threads for incoming connections
    and processing data, and then runs the user interface code

    :type addr: str
    :param addr: address of this server

    :type incoming_port: int
    :param incoming_port: port for incoming connects

    :type: max_proc: int
    :param: max_proc: maximum number of processor threads to use
    """

    def __init__(self, addr, incoming_port, max_proc=10, user="test_user"):
        self.max_processors = max_proc
        self.addr = addr
        self.incoming_port = incoming_port
        self.context = zmq.Context()
        self.proc_queue = Queue()
        from protocol import QuiltProtocol
        self.protocol = QuiltProtocol(self.addr, self.incoming_port, user)
        self.incoming = IncomingThread(self.incoming_port, self.proc_queue)
        self.incoming.setDaemon(True)
        for i in range(self.max_processors):
            t = ProcessorThread(self.proc_queue, self.protocol)
            t.start()

    def start(self):
        """Start the server and don't do anything else"""
        self.incoming.start()

    def start_with_ui(self):
        """
        Start the server and display and user interface
        """
        self.incoming.start()
        print "Welcome to Quilt"
        while True:
            user_in = raw_input(">>").split(" ")
            cmd = user_in[0]
            if cmd == "/connect":
                if len(user_in) != 3:
                    print "/connect <address> <port>"
                    continue
                self.protocol.connect_to_server(user_in[1], user_in[2])
            elif cmd == "/exit":
                self.terminate_threads()
                break
            else:
                self.protocol.send_msg(user_in[0], " ".join(user_in[1:]))

    def terminate_threads(self):
        """
        Terminates all threads except incoming threads which are auto killed on exit
        """
        for server in self.protocol.outgoing_queues:
            self.protocol.outgoing_queues[server].put(None)
        for i in range(self.max_processors):
            self.proc_queue.put(None)

def test_console():
    import sys
    if len(sys.argv) < 3:
        print "Usage: server.py <hostname> <port>"
        exit()
    s = QuiltServer(sys.argv[1], int(sys.argv[2]))
    s.start_with_ui()

if __name__ == "__main__":
    test_console()
