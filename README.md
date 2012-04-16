#QUILT
A distributed chat client intended for the Sugar environment.

#Core Ideas:
- Mesh network chat system 
- Dynamic peer discovery over the meshnet
- Routing that tolerates unstable nodes that may go offline randomly
- Easy to use and operate

#Protocol Ideas:
- protocol itself it loosely based on irc only with json
- all messages are JSON blobs
- Messages include:
	- JOIN <addr> <nick> <chan>
	- PART <addr> <nick> <chan>
	- MSG <addr> <nick> <chan/nick>
	- SERVERJOIN <addr> <capabilties> <connections>
	- SERVERPART <addr> <connections>

- Possible for channels to be zmq topics and clients simply subscribe to those topics

#Routing Ideas:

#Peer Discovery Ideas:
- Use the built in OLPC meshnetworking system
	- Tubes + dbus + olpc activity callbacks
- Use something based on avahi (skip all the olpc stuff)
- Write our own peer discovery system
