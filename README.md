#QUILT
A distributed chat client intended for the Sugar environment.
Licensed under the MIT License 

#Build Status:
Master: [![Build Status on master](https://secure.travis-ci.org/FOSSRIT/quilt.png?branch=master)](http://travis-ci.org/FOSSRIT/quilt)
Develop: [![Build Status on develop](https://secure.travis-ci.org/FOSSRIT/quilt.png?branch=develop)](http://travis-ci.org/FOSSRIT/quilt)

#Core Ideas:
- Mesh network chat system 
- Dynamic peer discovery over the meshnet
- Routing that tolerates unstable nodes that may go offline randomly
- Easy to use and operate

#Protocol:
- protocol itself it loosely based on irc
- protocol segments are seperated using zeromq multipart messages (act just like a list)
- protocol template: [routing, destination, command, *args]
	- routing is a comma seperated list of unique node names ie: node1,node2,node3
- Currently Implemented:
	- join
	- part
	- server_connect
	- ping
	- pong
	- message


#Routing Ideas:
- Routing is currently dumb, each message sent out has a comma seperated list of nodes it has been to, if a message returns to a node it has already been to, it is dropped
#Peer Discovery Ideas:
- Peer discovery is currently implemented using an avahi service

#Internals
- There are 3 main threads
	- IncomingThread which puts incoming messages into the processing queue
	- ProcessorThread which takes messages from the processing queue and handles them using a QuiltProtocol object
	- OutgoingThreads are assigned one per server and take messages from a given queue and send them to their assigned server
- Incoming message --> proc-queue -> processor thread -> server Dependant Outgoing Queue

#Dependancies:
	pyzmq-static

#Hacking

- clone it
- mkvirtualenv --system-site-packages quilt
- python setup.py develop
- quilt-console --help

#Test Suite

Either use nose directly::

  $ nosetests

Or use the setuptools command::

  $ python setup.py test
