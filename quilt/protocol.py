from Queue import Queue
from quilt import OutgoingThread


class QuiltProtocol(object):

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.outgoing_queues = {}

    def connect_to_server(self, server, port):
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
            self.outgoing_queues[server].put(
                [server, "server_connect", self.addr, self.port]
            )

    def ping_server(self, server):
        """
        Ping a specific server
        Next step in this implementation is to allow for pinging servers we
        are not directly connected to, this involves routing

        :type server: str
        :param server: The server to ping
        """

        if server in self.outgoing_queues:
            self.outgoing_queues.put([server, "ping", self.addr])

    def handle_server_connect(self, args):
        """
        Handle an incoming server connect, the incoming server sends us
        server-connect and then we do things like connect back to them
        args should look like this: [address, port]

        :type args: list
        :param args: A list of args that are recieved from the server
        """
        outgoing_addr = args[0]
        if not outgoing_addr in self.outgoing_queues:
            outgoing_port = int(args[1])
            new_queue = Queue()
            new_thread = OutgoingThread(
                outgoing_addr, outgoing_port, new_queue
            )
            new_thread.start()
            self.outgoing_queues[outgoing_addr] = new_queue
            self.outgoing_queues[outgoing_addr].put(
                ["server_connect", self.addr, self.port]
            )
            print "Server {0}:{1} connected to us".format(
                outgoing_addr, outgoing_port)

    def handle_ping(self, args):
        """
        Handle a ping from an incoming server
        format is [ping, sender]
        response is [pong, ourname]

        :type args: list
        :param args: A list of arguments for this command
        """
        server_name = args[0]
        if server_name in self.outgoing_queues:
            self.outgoing_queues.put([server_name, "pong", self.addr])

    def handle(self, dest, cmd, *args):
        """
        Handler method recieves a message and decided how to deal with it
        The protocol is split into parts: [destination, cmd, args...]
        Destination options are: all or a single server
        :type message: list
        :param dest: an address to send to
        :param cmd: a command to act on
        :param args: a list of arguments
        """

        # A little validation
        if not isinstance(args, (tuple, list)):
            raise ValueError("args must be list or tuple  not %r" % type(args))

        #Fill this in with a protocol implementation
        if hasattr(self, "handle_" + cmd):
            getattr(self, "handle_" + cmd)(args)
            self.handle_server_connect(args)
