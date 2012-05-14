from Queue import Queue
from quilt import OutgoingThread
from time import ctime
from models import QuiltUser, QuiltChannel

class QuiltProtocol(object):

    def __init__(self, addr, port, user):
        self.addr = addr
        self.port = port
        self.outgoing_queues = {}
        self.last_pongs = {}  #{server-name: last-pong}
        self.channels = {}
        self.user = QuiltUser(user, user)

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
            new_thread.setDaemon(True)
            new_thread.start()
            self.outgoing_queues[server] = new_queue
            self.outgoing_queues[server].put(
                [server, "server_connect", self.addr, self.port]
            )

    def send_join(self, user, channel):
        """
        Send the join command to all our connected servers

        :type user: str
        :param user: The user joining a channel

        :type channel: str
        :param channel: The channel the user is joining
        """

        for server in self.outgoing_queues:
            self.outgoing_queues[server].put(
                ["*", "join", user, channel]
            )

    def send_part(self, user, channel):
        """
        Send the part command to all connected servers

        :type user: str
        :param user: user sending the part command

        :type channel: str
        :param channel: channel the user is parting from
        """
        for server in self.outgoing_queue:
            self.outgoing_queues[server].put(
                ["*", "part", user, channel]
            )

    def send_message(self, user, channel, message):
        """
        Send a chat message from the specified user,
        to the specified channel

        :type user: str
        :param user: user sending the message

        :type channel: str
        :param channel: channel to send message to

        :type message: str
        :param: message: message to be sent
        """

        for server in self.outgoing_queues:
            self.outgoing_queues[server].put(
                ["*", "message", user, channel, message]
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
            self.outgoing_queues[server].put([server, "ping", self.addr])

    def handle_server_connect(self, outgoing_addr, outgoing_port):
        """
        Handle an incoming server connect, the incoming server sends us
        server-connect and then we do things like connect back to them
        args should look like this: [address, port]

        :type outgoing_addr: str
        :param outgoing_addr: Address of the outgoing address
        :type outgoing_port: str (or int)
        :param outgoing_port: Address of the outgoing port
        """
        if not isinstance(outgoing_port, int):
            outgoing_port = int(outgoing_port)

        if not outgoing_addr in self.outgoing_queues:
            new_queue = Queue()
            new_thread = OutgoingThread(
                outgoing_addr, outgoing_port, new_queue
            )
            new_thread.start()
            self.outgoing_queues[outgoing_addr] = new_queue
            self.outgoing_queues[outgoing_addr].put(
                [outgoing_addr, "server_connect", self.addr, self.port]
            )
            print "Server {0}:{1} connected to us".format(
                outgoing_addr, outgoing_port)

    def handle_ping(self, server_name):
        """
        Handle a ping from an incoming server
        format is [ping, sender]
        response is [pong, ourname]

        :type server_name: str
        :param server_name: The server to ping
        """
        if server_name in self.outgoing_queues:
            self.outgoing_queues[server_name].put([server_name, "pong", self.addr])
        else:
            raise ValueError(
                "%r is not a server I am configured to ping." % server_name)

    def handle_pong(self, server_name):
        """
        Handle the returning pong from a server we have pinged

        :type server_name: str
        :param server_name: address of the server sending us a pong
        """

        if server_name in self.outgoing_queues:
            self.last_pongs[server_name] = ctime()

    def handle_message(self, user, channel, message):
        """
        Handle a chat message sent from some one else on the network
        messages are sent to specific rooms so only people in that channel see the message

        :type user: str
        :param user: username (nick) of the person sending the message

        :type channel: str
        :param channel: channel to send message to (used in filtering who recieves the message)

        :type message: str
        :param message: the actual message being sent
        """

        """
        This needs pass the message back to the UI handling bits so it can display the message
        """
        pass

    def handle_join(self, user, channel):
        """
        Handle a message sent out when a user joins a channel
        It seems like every node is going to need to keep this value for every channel
        That way when a user joins a new channel they have all the users in that channel already

        :type user: str
        :param user: The user joining the channel

        :type channel: str
        :param channel: the channel the user is joining
        """

        if channel in self.channels:
            self.channels[channel].addUser(user)
        else:
            self.channels[channel] = QuiltChannel(channel)
            self.channels[channel].addUser(user)

    def handle_part(self, user, channel):
        """
        Handle the part command being sent by a user
        This is very similar to handle_join, it updates a dict of some kind with all the channels

        :type user: str
        :param user: user parting the channel

        :type channel: str
        :param channel: channel user is parting from
        """

        if channel in self.channels:
            self.channels[channel].removeuser(user)
            if len(self.channels[channel].users) == 0:
                del self.channels[channel]

    def handle(self, dest, cmd, *args):
        """
        Handler method recieves a message and decided how to deal with it
        The protocol is split into parts: [destination, cmd, args...]
        Destination options are: all or a single server
        :type dest: str
        :param dest: an address to send to
        :type cmd: str
        :param cmd: a command to act on
        :type args: list
        :param args: a list of arguments
        """


        # A little validation
        if not isinstance(args, (tuple, list)):
            raise ValueError("args must be list or tuple  not %r" % type(args))

        #Fill this in with a protocol implementation
        if hasattr(self, "handle_" + cmd):
            getattr(self, "handle_" + cmd)(*args)
        else:
            raise ValueError("No such command %r (handle_%s)" % (cmd, cmd))
