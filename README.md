#QUILT
A distributed chat client intended for the Sugar environment.

#Protocol Ideas:
-    protocol itself it loosely based on irc only with json
-    all messages are JSON blobs
-    Messages include:
	-    JOIN <addr> <nick> <chan>
	-    PART <addr> <nick> <chan>
	-    MSG <addr> <nick> <chan/nick>
	-    SERVERJOIN <addr> <capabilties> <connections>
	-    SERVERPART <addr> <connections>

-   Possible for channels to be zmq topics and clients simply subscribe to those topics
