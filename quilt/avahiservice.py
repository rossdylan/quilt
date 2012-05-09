""" 
    Avahi Network Service Scripting
"""
import Queue
import threading
import avahi, dbus, gobject
from dbus import DBusException 
from dbus.mainloop.glib import DBusGMainLoop

__all__ = ["QuiltAvahiServer", "QuiltAvahiClient"]

TYPE = '_quilt._tcp'

class QuiltAvahiNode(object): 
    """ Quilt Avahi Connection Node, represents a 
    found connection, and its connection details. """
    def __init__(self, domain="local", hostname="none", address="", port=""): 
        """ Construct Connection Node """
        self.domain = domain
        self.hostname = hostname
        self.address = address
        self.port = port
    
    def __str__(self): 
        """ String representation. """
        return "Quilt Avahi Connection Node:\n -domain: %s\n -hostname: %s\n -address: %s\n -port: %s\n"\
                    % (self.domain, self.hostname, self.address, self.port)

from threading import Thread
class QuiltAvahiClient(Thread): 
    """ Qulit's Avahi Service Discovery Object """
  
    def __init__(self): 
        """ Construct Search Client """
        threading.Thread.__init__(self)
        self.Nodes = Queue.Queue()
        self.loop = DBusGMainLoop()
        self.bus = dbus.SystemBus(mainloop = self.loop)
       
        self.server = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, '/'), 
            'org.freedesktop.Avahi.Server')

        self.sbrowser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, 
            self.server.ServiceBrowserNew(avahi.IF_UNSPEC, 
                avahi.PROTO_UNSPEC, TYPE, 'local', dbus.UInt32(0))), 
            avahi.DBUS_INTERFACE_SERVICE_BROWSER)

    def resolve(self, *args): 
        """ 
            :param args: Arguments of the resolved service
            :type  args: Array of mixed string and integer arguments. 
        """
        # Handle Connection Pattern Here, for now just print that we found 
        # the service #TODO
        node = QuiltAvahiNode(args[4], args[5].split('.')[0], args[7], args[8])
        print node
        self.Nodes.put(node)
        
    def error(self, *args): 
        """
            :param args: Arguments of the error in the resolved service
            :type  args: Mixed strings and integers
        """
        print "Error: %s" % args[0]
    
    def search_handler(self, interface, protocol, name, stype, domain, flags):
        """ Handles the finding of a service on the local network. 
            :param  interface:  Interface Name
            :type   interface:  String
            :param  protocol:   Protocol Type
            :type   protocol:   String
            :param  name:       Name of service
            :type   name:       String
            :param  stype:      Service Type
            :type   stype:      String
            :param  domain:     Domain of service
            :type   domain:     String
            :param  flags:      Flags of the Service
            :type   flags:      int
        """
        print "Service Found %s type %s domain %s" % (name, stype, domain)
         
        # We can determine if the service is local, avoiding uncessary connections
        if flags & avahi.LOOKUP_RESULT_LOCAL: 
            # TODO: Handle local service here 
            pass

        self.server.ResolveService(interface, protocol, name, stype, domain, 
                avahi.PROTO_UNSPEC, dbus.UInt32(0), 
                reply_handler=self.resolve, error_handler=self.error)

    def run(self): 
        """ Searches the local network for broadcasting avahi services, 
            handles found services in the resolved method 
        """
        self.sbrowser.connect_to_signal("ItemNew", self.search_handler)
        gobject.MainLoop().run()

class QuiltAvahiServer(object): 
    """ Quilt's Avahi Server Object
        NOTE: Ports 9375-9379 should be our target ports
    """
    def __init__(self, name="Quilt", port=9375, stype="_quilt._tcp", 
                    domain="", host="", text=""): 
            """
                Construct the avahi service
                :type name: string
                :param name: name of service
                :type port: int
                :param port: port to be run on. 
                :type stype: str
                :param stype: service type
                :type domain: str
                :param domain: service domain
                :type host: str
                :param host: service host
                :type text: --
                :param text: --
            """
            self.name = name
            self.stype = stype
            self.domain = domain
            self.host = host
            self.port = port
            self.text = text

    def publish(self): 
        """ Make the service discoverable on the network """
        bus = dbus.SystemBus()
        server = dbus.Interface(
                bus.get_object(
                    avahi.DBUS_NAME, 
                    avahi.DBUS_PATH_SERVER), 
                avahi.DBUS_INTERFACE_SERVER)

        interface = dbus.Interface(
                bus.get_object(avahi.DBUS_NAME, 
                    server.EntryGroupNew()), 
                avahi.DBUS_INTERFACE_ENTRY_GROUP)
        
        interface.AddService(
                avahi.IF_UNSPEC, 
                avahi.PROTO_UNSPEC, 
                dbus.UInt32(0), 
                self.name, 
                self.stype, 
                self.domain, 
                self.host, 
                dbus.UInt16(self.port), 
                self.text)

        interface.Commit()
        self.group = interface

    def unpublish(self): 
        """ Remove the service """
        self.group.Reset()
