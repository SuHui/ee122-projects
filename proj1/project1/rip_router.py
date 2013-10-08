from sim.api import *
from sim.basics import *
from collections import defaultdict

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):
        # we need to create a routing table containing what we believe to be all of the shortest distances
        # and corresponding next hops. I'm going with a dict representation for now on. first dict key is the dest
        # and second key is the next hop.
        self.routing_table = defaultdict(lambda: defaultdict(lambda:float('inf')))
        self.ports = {}
        pass

    def handle_rx (self, packet, port):
        # three cases of packet we can get, DiscoveryPacket, RoutingUpdate, and other Packet
        if isinstance(packet, DiscoveryPacket):
        	handle_dp(packet, port)
        elif isinstance(packet, RoutingUpdate):
        	handle_ru(packet, port)

        raise NotImplementedError
    
    # after receiving a discovery packet
    def handle_dp(self, packet, port):
    	if packet.is_link_up:
    		self.routing_table[packet.src][port] = packet.latency
    		self.ports[port] = packet.src
    	else:
    		for key in self.routing_table.keys():
	    		self.routing_table[key][port] = float("inf")
	    	del self.ports[port]

    # after receiving a routing update packet
    def handle_ru(self, packet, port):
    	src = packet.src
    	for (key, value) in packet.paths.iteritems():
    		current_dist = self.routing_table[src][port]
    		if self.routing_table[key][port] == float('inf') or value+current_dist < self.routing_table[key][port]:
    			self.routing_table[key][port] = value + current_dist
    	return "this one doesn't sound as funny"
   