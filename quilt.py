try:
    import zmq
except:
    print "Error, you don't have pyzmq installed"
from threading import Thread
from Queue import Queue


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
        super(IncomingThread, self).__init__()

    def run(self):
        self.incoming.bind("tcp://*:{0}".format(self.listen_port))
        while True:
            data = self.incoming.recv_multipart()
            self.proc_queue.put(data)
            self.incoming.send("ack")#probably should change this to something proper


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
            data = self.proc_queue.get()
            #Somehow in this section we need to do protocol parsing
            self.protocol.handle(data)


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
        self.address = "tcp://{0}:{1}".format(addr,port)
        self.queue = queue
        self.context = zmq.Context()
        self.outgoing = self.context.socket(zmq.REQ)

    def run(self):
        self.outgoing.connect(self.address)
        while True:
            data = [str(i) for i in self.queue.get()]
            self.outgoing.send_multipart(data)
            self.outgoing.recv() #Get our ACK


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

    def __init__(self, addr, incoming_port, max_proc=10):
        self.max_processors = max_proc
        self.addr = addr
        self.incoming_port = incoming_port
        self.context = zmq.Context()
        self.proc_queue = Queue()
        self.protocol = QuiltProtocol(self.addr,self.incoming_port)
        self.incoming = IncomingThread(self.incoming_port, self.proc_queue)
        for i in range(self.max_processors):
            t = ProcessorThread(self.proc_queue,self.protocol)
            t.start()

    def start(self):
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
            else:
               self.protocol.send_msg(user_in[0], " ".join(user_in[1:]))

class QuiltProtocol(object):

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.outgoing_queues = {}

    def connect_to_server(self,server, port):
        """
        Connect to a server

        :type server: str
        :param server: server address

        :type port: int
        :param port: port number of the server
        """

        if not server in self.outgoing_queues:
            new_queue = Queue()
            new_thread = OutgoingThread(server, port, new_queue)
            new_thread.start()
            self.outgoing_queues[server] = new_queue
            self.outgoing_queues[server].put(["server_connect", self.addr, self.port])

    def handle_server_connect(self,args):
        """
        Handle an incoming server connect, the incoming server sends us server-connect
        and then we do things like connect back to them

        :type args: list
        :param args: A list of args that are recieved from the server
        """
        outgoing_addr = args[0]
        if not outgoing_addr in self.outgoing_queues:
            outgoing_port = int(args[1])
            new_queue = Queue()
            new_thread = OutgoingThread(outgoing_addr, outgoing_port, new_queue)
            new_thread.start()
            self.outgoing_queues[outgoing_addr] = new_queue
            self.outgoing_queues[outgoing_addr].put(["server_connect", self.addr, self.port])
            print "Server {0}:{1} connected to us".format(outgoing_addr, outgoing_port)

    def handle(self, message):
        """
        Handler method recieves a message and decided how to deal with it
        The protocol is split into parts: [destination, cmd, args...]
        Destination options are: all or a single server
        :type message: list
        :param message: a list of data recieved from a zeromq recv_multipart
        """

        assert type(message) == type(list())
        #Fill this in with a protocol implementation
        cmd = message[0]
        args = message[1:]
        if hasattr(self,"handle_" + cmd):
            getattr(self,"handle_" + cmd)(args)
            self.handle_server_connect(args)



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "Usage: server.py <hostname> <port>"
        exit()
    s = QuiltServer(sys.argv[1], int(sys.argv[2]))
    s.start()
