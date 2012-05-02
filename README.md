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
- If we do continue on with json we might want to use a faster json parser
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

#Internals
-[NOTE] Queues are to hopefully work around threading funky-ness
- Single Thread handles incoming requests and puts them into a queue to be processed
    - Queue handlers then process the data and determine what to do with it
        - This could include forwarding messages to all outgoing
            - Put the message into the outgoing queue for whatever server it needs to go to
- Incoming message --> proc-queue -> processor thread -> server Dependant Outgoing Queue

#Dependancies:
- pyzmq (pip install zmq)
	- libevent
	- zeromq

#Hacking

- clone it
- mkvirtualenv --system-site-packages quilt
- python setup.py develop
- quilt-console --help
