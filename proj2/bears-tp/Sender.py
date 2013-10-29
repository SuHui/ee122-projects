import sys
import getopt

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.payload_size = 1444

    # Main sending loop.
    def start(self):
        print "starting"
        print self.payload_size
        print self.dest
        print self.dport
        seqno = 0
        while True:
            data = self.infile.read(self.payload_size)
            # our packet has less data than our payload size, so it's the last one!
            if len(data) < self.payload_size:
                message = self.make_packet("end", seqno, data)
                break
            if seqno == 0:
                message = self.make_packet("start", seqno , data)
            else:
                message = self.make_packet("data", seqno, data)

            #send
            self.send(message)

            seqno = seqno + 1
            #wait



        # have some timeout check

        # getting the checksum, and appending it to the message.
        

    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        # invalid checksum
        if not Checksum.validate_checksum(ack):
            pass
        msg_type, seqno, data, checksum = self.split_packet(ack)
        

    def handle_dup_ack(self, ack):
        # invalid checksum
        if not Checksum.validate_checksum(ack):
            pass
        msg_type, seqno, data, checksum = self.split_packet(ack)

    def log(self, msg):
        if self.debug:
            print msg

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
