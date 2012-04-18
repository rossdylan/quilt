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

    def __init__(self, proc_queue, outgoing_queues):
        super(ProcessorThread, self).__init__()
        self.proc_queue = proc_queue
        self.outgoing_queue = outgoing_queues

    def run(self):
        while True:
            data = self.proc_queue.get()
            print data #Replace with actually processing

class QuiltServer(object):

    def __init__(self, incoming_port):
        self.incoming_port
        self.context = zmq.Context()
        self.proc_queue = Queue()
        self.outgoing_queues = {}
        """
            Note on outgoing_queues:
            When a new server connects we assign it a queue so we can then route messages to it properly
        """
        self.incoming = IncomingThread(self.incoming_port, self.proc_queue)

    def start(self):
        self.incoming.start()

