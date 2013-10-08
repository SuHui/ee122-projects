from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):
        # we need to create a routing table containing what we believe to be all of the shortest distances
        # and corresponding next hops.
        pass

    def handle_rx (self, packet, port):
        # three cases of packet we can get, DiscoveryPacket, RoutingUpdate, and other Packet
        if isinstance(packet, DiscoveryPacket):
        	handle_dp(packet)
        elif isinstance(packet, RoutingUpdate):
        	handle_ru(packet)

        raise NotImplementedError
    
    def handle_dp(self, packet):
    	if packet.is_link_up:
    		print "we have a new link. and its latency is", packet.latency
    	else:
    		print "LINK DOWN. I REPEAT, LINK DOWN"
    	return "hahahaha, dp"
    def handle_ru(self, packet):
    	return "this one doesn't sound as funny"
   