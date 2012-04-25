""" 
	Avahi Network Service Scripting
"""

import avahi
import dbus 

class QuiltAvahiService(object): 
	""" Quilt's Zeroconf Network Service 
		NOTE: Ports 9375-9379 should be our target ports
	"""
	def __init__(self, name="Quilt", port=9375, stype="_http._tcp", 
					domain="", host="", text=""): 
			self.name = name
			self.stype = stype
			self.domain = domain
			self.host = host
			self.port = port
			self.text = text

	def publish(self): 
		pass		
