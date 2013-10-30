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
        # 500 milliseconds
        self.timeout = .500
        self.window_size = 5
        self.s_window = {}
        self.window = (0, self.window_size - 1)
        self.end = float('inf')

    # Main sending loop.
    def start(self):
        seqno = 0
        while True:
            #while next packet is within our sending window
            while seqno <= self.window[1]:
                if seqno > self.end:
                    break

                if seqno in self.s_window.keys():
                    message = self.s_window[seqno]
                else: 
                    data = self.infile.read(self.payload_size)
                    # our packet has less data than our payload size, so it's the last one!
                    if len(data) < self.payload_size:
                        self.end = seqno
              #          print "sent end packet at", seqno
                        message = self.make_packet("end", seqno, data)
                    if seqno == 0:
                        message = self.make_packet("start", seqno , data)
                    else:
                        message = self.make_packet("data", seqno, data)

                #send
                self.send(message)
                self.s_window[seqno] = message
                seqno += 1
            
            ack = self.receive(self.timeout)
            #print "ack received", ack

            # if not a timeout...
            if ack != None:
                if not Checksum.validate_checksum(ack):
                    continue
                ack_seqno = int(ack.split('|')[1])

                if ack_seqno > self.window[0]:
                    self.handle_new_ack(ack)
                        # this is an end packet
                    if ack_seqno > self.end:
                        break
                else:
                    self.handle_dup_ack(ack)
            else:
             #   print "TIMEOUT!!!", seqno
                seqno = self.window[0]
                continue
                



        # have some timeout check
        

    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        ack_seqno = int(ack.split('|')[1])
        for key in self.s_window.keys():
            if key < ack_seqno:
                del self.s_window[key]
        self.window = (ack_seqno, ack_seqno+self.window_size) if ack_seqno != (self.end + 1) else (ack_seqno, ack_seqno)
        

    def handle_dup_ack(self, ack):
        # invalid checksum
        if not Checksum.validate_checksum(ack):
            pass
        msg_type, seqno, data, checksum = self.split_packet(ack)
        if int(seqno) > self.window[0]:
            self.send(self.s_window[seqno])

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
