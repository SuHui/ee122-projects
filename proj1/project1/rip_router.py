from sim.api import *
from sim.basics import *
from collections import defaultdict

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):
        # maps all possible destinations -> dicts where the keys are next_hops and values are distances using that hop.
        self.routing_table = defaultdict(lambda: defaultdict(lambda:float('inf')))
        # maps ports -> corresponding entities
        self.ports = {}
        # maps desired destinations -> next hop port
        self.paths = {}
        # maps desired destinations - > minimum distance. this is the same as a routingupdate.paths
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
            self.routing_table[packet.src][port] = 1
            self.paths[packet.src] = port
            self.ports[port] = packet.src
            update = self.updatepaths(packet.src, 1, port)
            if update:
                self.send_ru()
        else:
            for key in self.routing_table.keys():
                print "setting the table at", key, port, "to inf"
                self.routing_table[key][port] = float("inf")
                print "at", key, "row looks like", [(k,v) for (k,v) in self.routing_table[key].items()]

            del self.ports[port]
            self.recompute(*self.routing_table.keys())

    # after receiving a routing update packet
    def handle_ru(self, packet, port):
        print self, " is handling a routingupdate from", packet.src
        update = False
        update_items = packet.paths.keys()
        print self, "handling an update...", [(k,v) for (k,v) in packet.paths.items()]

        for dest in update_items:
            self.routing_table[dest][port] = packet.paths[dest] + 1
            update = self.updatepaths(dest, self.routing_table[dest][port], port) or update
        for dest, row in self.routing_table.iteritems():
            # -----------------------------------------------------------------------
            # -----------------------------------------------------------------------# -----------------------------------------------------------------------
            # -----------------------------------------------------------------------
            if dest not in update_items: # and dest != packet.src: #<------------------------ THIS IS AN ERROR WHETHER IT IS COMMENTED OUT OR LEFT IN. ADDRESS THIS.
            # -----------------------------------------------------------------------
            # -----------------------------------------------------------------------# -----------------------------------------------------------------------
            # -----------------------------------------------------------------------
                row[port] = float('inf')
            update = self.updatepaths(dest, self.routing_table[dest][port], port) or update

        if update:
            self.send_ru()

    def updatepaths(self, dest, dist, port):
        if dist < self.distances[dest]:
            self.distances[dest] = dist
            self.paths[dest] = port
            # true means our internal distances changed, so we need to send an update.
            return True
        # return false because our distance doesn't change
        elif dist == self.distances[dest]:
            self.paths[dest] = min(port, self.paths[dest])
        # if we are getting a routing update from the port we currently think is the best port to take from a path, 
        # we might need to change our best distances
        elif self.paths[dest] == port:
            self.recompute(dest)
        return False

    def send_ru(self):
        for (port,dest) in self.ports.iteritems():
            update = RoutingUpdate()
            for entity, distance in self.distances.iteritems():
                # do not broadcast paths to ourself, our destination, the next hop for a given destination, or if we have no such path.
                if entity not in [self, dest, self.ports[self.paths[dest]]] or (distance == float('inf')):
                    update.add_destination(entity, distance)
            self.send(port=port,packet=update)

    def recompute(self, *args):
        for dest in args:
            options = self.routing_table[dest]
            best = min([(port, d) for (port, d) in options.iteritems()], key = lambda x: x[1])
            self.distances[dest] = best[1]
            self.paths[dest] = best[0]


        self.send_ru()
