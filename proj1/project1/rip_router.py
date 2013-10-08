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
        # and second key is the nevxt hop.
        self.routing_table = defaultdict(lambda: defaultdict(lambda:float('inf')))
        self.ports = {}
        self.paths = {}
        self.distances = defaultdict(lambda : float('inf'))
        self.distances[self] = 0

    def handle_rx (self, packet, port):
        # three cases of packet we can get, DiscoveryPacket, RoutingUpdate, and other Packet
        if isinstance(packet, DiscoveryPacket):
            self.handle_dp(packet, port)
        elif isinstance(packet, RoutingUpdate):
            self.handle_ru(packet, port)
        else:
            # send the packet to the corresponding port for our destination.
            self.send(packet=packet, port=self.paths[packet.dst])
    
    # after receiving a discovery packet
    def handle_dp(self, packet, port):
        print self, " is handling a discovery packet from", packet.src
        if packet.is_link_up:
            self.routing_table[packet.src][port] = packet.latency
            self.ports[port] = packet.src
            update = self.updatepaths(packet.src, packet.latency, port)
            if update:
                self.send_ru()
        else:
            for key in self.routing_table.keys():
                self.routing_table[key][port] = float("inf")
            del self.ports[port]

    # after receiving a routing update packet
    def handle_ru(self, packet, port):
        print self, " is handling a routingupdate from", packet.src
        src, update = packet.src, False
        for (key, value) in packet.paths.iteritems():
            current_dist = self.routing_table[src][port]
            if self.routing_table[key][port] == float('inf') or value+current_dist < self.routing_table[key][port]:
                self.routing_table[key][port] = value + current_dist
                update = self.updatepaths(key, value + current_dist, port) or update
        if update:
            self.send_ru()

    def updatepaths(self, src, dist, port):
        if dist < self.distances[src]:
            self.distances[src] = dist
            self.paths[src] = port
            return True
        return False

    def send_ru(self):
        for (port,dest) in self.ports.iteritems():
            print self, "is sending a router update packet to", port
            update = RoutingUpdate()
            for entity, distance in self.distances.iteritems():
                if entity not in [self, dest]:
                    update.add_destination(entity, distance)
            self.send(port=port,packet=update)