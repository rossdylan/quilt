""" 
    Avahi Network Service Scripting
"""

import avahi
import dbus 

__all__ = ["QuiltAvahiService"]

class QuiltAvahiService(object): 
    """ Quilt's Zeroconf Network Service 
        NOTE: Ports 9375-9379 should be our target ports
    """
    def __init__(self, name="Quilt", port=9375, stype="_ftp._tcp", 
                    domain="", host="", text=""): 
            self.name = name
            self.stype = stype
            self.domain = domain
            self.host = host
            self.port = port
            self.text = text

    def publish(self): 
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
        self.group.Reset()

if __name__ == "__main__": 
    serv = QuiltAvahiService()
    serv.publish()
    raw_input("Press a key to kill...")
    serv.unpublish()
