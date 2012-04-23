import zmq
from threading import Thread
from Queue import Queue


class IncomingThread(Thread):

    def __init__(self, listen_port, proc_queue):
        self.listen_port = listen_port
        self.proc_queue = proc_queue
        self.context = zmq.Context()
        self.incoming = self.context.Socket(zmq.REP)
        super(IncomingThread, self).__init__()

    def run(self):
        self.incoming.bind("tcp://*:{0}".format(self.listen_port))
        while True:
            data = self.incoming.recv_multipart()
            self.proc_queue.put(data)
            self.incoming.send("ack")#probably should change this to something proper


class ProcessorThread(Thread):

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

    def __init__(self, addr, port, queue):
        self.address = "tcp://{0}:{1}".format(addr,port)
        self.queue = queue
        self.context = zmq.Context()
        self.outgoing = self.context.Socket(zmq.REQ)

    def run(self):
        self.outgoing.connect(self.address)
        while True:
            data = self.queue.get()
            self.outgoing.send_multipart(data)
            self.outgoing.recv() #Get our ACK


class QuiltServer(object):

    def __init__(self, incoming_port, max_proc=10):
        self.max_processors = max_proc
        self.incoming_port
        self.context = zmq.Context()
        self.proc_queue = Queue()
        self.protocol = QuiltProtocol()
        """
            Note on outgoing_queues:
            When a new server connects we assign it a queue so we can then route messages to it properly
        """
        self.incoming = IncomingThread(self.incoming_port, self.proc_queue)
        for i in range(self.max_processors):
            t = ProcessorThread(self.proc_queue,self.protocol)
            t.start()

    def start(self):
        self.incoming.start()

class QuiltProtocol(object):

    def __init__(self):
        self.outgoing_queues = {}

    def handle(self, message):
        assert type(message) == type(list())
        #Fill this in with a protocol implementation
        extra = message[0] #this could hold routing things
        cmd = message[1]
        args = message[2:]
        if cmd == "server-connect": #A new server connects
            outgoing_addr = args[0]
            if not outgoing_addr in self.outgoing_queues:
                outgoing_port = args[1]
                new_queue = Queue()
                new_thread = OutgoingThread(outgoing_addr, outgoing_port, new_queue)
                new_thread.start()
                self.outgoing_queues[outgoing_addr] = new_queue
