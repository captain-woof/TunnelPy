import socket
import argparse
import threading
import random


class TunnelPy:
    def __init__(self, mhost, mport, dhost, dport, verbose, quiet,timeout):
        self.timeout = timeout  # recv timeout
        self.backlog = 30  # how many pending connections queue will hold
        self.buffer = 2048  # Receive in chunks

        self.mhost = mhost
        self.mport = mport
        self.dhost = dhost
        self.dport = dport

        self.middle_man = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.verbose = verbose
        self.quiet = quiet

        self.colorAndFormat = ColorAndFormat()

    def on_receive(self, csock, caddr, random_id):  # Thread callback
        # Receive req from client
        try:
            data_bytes = []
            while True:
                try:
                    data = csock.recv(self.buffer)
                    if len(data) == 0:
                        break
                    data_bytes.append(data)
                except socket.timeout:
                    break
            data = b"".join(data_bytes)

            if len(data) == 0:
                if not self.quiet:
                    print(self.colorAndFormat.Bluebg("[>>] Blank request received from client " + caddr[0] + ':' + str(
                        caddr[1]) + ' | ID:#' + random_id))
                    print(self.colorAndFormat.Yellowbg2("[!] Hence, taking no action") + '\n')
                return

        except Exception as e:
            if csock:
                csock.shutdown(0)
            print(self.colorAndFormat.Redbg(str(e)))
            return

        if not self.quiet:
            print(self.colorAndFormat.Bluebg(
                "[>>] Received request from client " + caddr[0] + ':' + str(caddr[1]) + ' | ID:#' + random_id) + '\n')
            if self.verbose:
                try:
                    print(self.colorAndFormat.Blue2(data.decode() + '\n'))
                except UnicodeDecodeError:
                    print(self.colorAndFormat.Yellowbg2("[!] Cannot display received request here"))

        # Forward req to dhost:dport
        mtd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mtd.connect_ex((self.dhost, self.dport))
        try:
            mtd.sendall(data)
            if self.verbose:
                print(self.colorAndFormat.Orangebg(
                    "[->] Relayed to " + self.dhost + ':' + str(self.dport) + ' | ID:#' + random_id) + '\n')
        except Exception as e:
            if mtd:
                mtd.shutdown(0)
            if csock:
                csock.shutdown(0)
            print(self.colorAndFormat.Redbg(str()))
            return

        # Receive reply from dhost:dport
        try:
            data_bytes = []
            while True:
                try:
                    data = mtd.recv(self.buffer)
                    if len(data) == 0:
                        break
                    data_bytes.append(data)
                except socket.timeout:
                    break
            data = b"".join(data_bytes)

            if not data:
                if not self.quiet:
                    print(self.colorAndFormat.Greenbg2("[!] Blank reply received from " + self.dhost + ':' + str(
                        self.dport) + ' | ID:#' + random_id) + '\n')
                return

            if self.verbose:
                print(self.colorAndFormat.Greenbg2(
                    "[<-] Received reply from " + self.dhost + ':' + str(self.dport) + ' | ID:#' + random_id))
                try:
                    print(self.colorAndFormat.Green2(data.decode() + '\n'))
                except UnicodeDecodeError:
                    print(self.colorAndFormat.Redbg("[!] Cannot display received reply"))

        except Exception as e:
            if mtd:
                mtd.shutdown(0)
            if csock:
                csock.shutdown(0)
            print(self.colorAndFormat.Redbg(str(e)))
            return

        # forward to client
        try:
            csock.sendall(data)
        except Exception as e:
            print(self.colorAndFormat.Redbg(str(e)))
            return

        # Closing connections
        try:
            mtd.shutdown(0)
            csock.shutdown(0)
            if not self.quiet:
                print(
                    self.colorAndFormat.Orangebg("[✓] Relayed reply to client successfully! | ID:#" + random_id) + '\n')
        except Exception as e:
            print(self.colorAndFormat.Redbg(str(e)))

    def start_listener(self):
        try:
            self.middle_man.bind((self.mhost, self.mport))
            self.middle_man.listen(self.backlog)
        except Exception as e:
            print(self.colorAndFormat.Redbg('Port ' + str(self.mport) + ' is already in use!'))
            return
        print(self.colorAndFormat.Orangebg(banner) + '\n')

        print(self.colorAndFormat.Yellowbg2("GLOBAL TIMEOUT: " + str(self.timeout) + ' second(s)'))

        if self.verbose:
            print(self.colorAndFormat.Yellowbg2("VERBOSE MODE: ON"))
        else:
            print(self.colorAndFormat.Yellowbg2("VERBOSE MODE: OFF"))

        if self.quiet:
            print(self.colorAndFormat.Yellowbg2("QUIET MODE: ON"))
        else:
            print(self.colorAndFormat.Yellowbg2("QUIET MODE: OFF"))

        print(self.colorAndFormat.Selected("[..] Listening on [any] on port " + str(self.mport) + '\n'))

        # Server spin
        while True:
            try:
                random_id = str(random.randint(1, 999999))
                client_sock, client_addr = self.middle_man.accept()
                client_sock.settimeout(self.timeout)
                thread = threading.Thread(target=self.on_receive, args=(client_sock, client_addr, random_id))
                thread.start()

            except KeyboardInterrupt:
                if self.middle_man:
                    self.middle_man.shutdown(0)
                print(self.colorAndFormat.Selected("\n[✓] TunnelPy server stopped!"))
                break

            except Exception as e:
                if self.middle_man:
                    self.middle_man.shutdown(0)
                print(self.colorAndFormat.Redbg(str(e)))
                break


class ColorAndFormat:
    def __init__(self):
        # Format
        self.__selected = '\33[7m'
        self.__reset = '\033[0m'
        self.__blue2 = '\33[94m'
        self.__redbg = '\33[41m'
        self.__bold = '\33[1m'
        self.__greenbg2 = '\33[102m'
        self.__green2 = '\33[92m'
        self.__orangebg = '\33[100m'
        self.__bluebg = '\33[44m'
        self.__yellowbg2 = '\33[103m'

    def Bold(self, text):
        return self.__bold + text + self.__reset

    def Green2(self, text):
        return self.__green2 + text + self.__reset

    def Yellowbg2(self, text):
        return self.__bold + self.__yellowbg2 + text + self.__reset

    def Orangebg(self, text):
        return self.__bold + self.__orangebg + text + self.__reset

    def Greenbg2(self, text):
        return self.__bold + self.__greenbg2 + text + self.__reset

    def Selected(self, text):
        return self.__selected + text + self.__reset

    def Blue2(self, text):
        return self.__blue2 + text + self.__reset

    def Redbg(self, text):
        return self.__bold + self.__redbg + text + self.__reset

    def Bluebg(self, text):
        return self.__bold + self.__bluebg + text + self.__reset


# Just a banner
banner = """
 _____                       _ ____        
|_   _|   _ _ __  _ __   ___| |  _ \ _   _ 
  | || | | | '_ \| '_ \ / _ \ | |_) | | | |
  | || |_| | | | | | | |  __/ |  __/| |_| |
  |_| \__,_|_| |_|_| |_|\___|_|_|    \__, |
                                     |___/ """

# The args
description = """TunnelPy simply exposes any service, running internally in a network/host, 
to the outside, by making a tunnel through sockets. Use '--help' for details on how to use
this, or '--examples' for examples.
"""
usage = """
You can run this script on any host that you'd like to use as the middle-man, and 
choose a port on the host that is allowed by the firewall to the outside, and you
can then simply use this mport on the middle-man host to forward your data to any
chosen dhost:dport connected to the middle-man host, INCLUDING (obviously) the same
host itself.

In other words, mport (middle-man's port) will be available for you to send data
to/receive data from, and it'd act as if you sent/received the data to/from
dhost:dport (destination host's ip and port). This makes a data tunnel between
the client, the TunnelPy server as the middle-man, and the dhost:dport.

Also, the TunnelPy server uses threading, so you can send multiple requests, and
each one of them will be handled completely in an entire new thread of its own.

Arguments:
--tunnel      : Precede the tunnelpy host and port arguments by this
                Format: --tunnel <mport>:<dhost ip>:<dport>
--verbose, -v : Start the tunnelpy server in verbose mode (shows the data in transit)
--quiet, -q   : Start the tunnelpy server in verbose mode (shows no transit information)
--timeout, -t : Set the global timeout for receiving data (default: 1 second)
--help, -h    : Get this help message
--examples    : See some usage examples
"""

examples = """
Example 1:
----------
Say you are at 10.0.0.3, and 10.0.0.8 has an internal service running on its loopback interface
on port 7878. You want to have this service exposed on its accessible interface on port 4444.
For this, you execute the script on 10.0.0.8 as:

tunnel.py -v --tunnel 4444:127.0.0.1:7878

This will establish a tunnel between 10.0.0.8:4444 <--> 127.0.0.1:7878, and you can
communicate with 10.0.0.8:4444 to actually talk to 127.0.0.1:7878. Do note that you
will also see the request and response data in transit because of '-v'.


Example 2:
----------
Say you are at 10.0.0.3, and 10.0.0.8 is allowed by firewall to access a service running on
port 7878 of another host 10.0.0.16 (connected to 10.0.0.8), but you are not. You can only
access 10.0.0.8. You cannot directly access this from 10.0.0.3, but using 10.0.0.8 as the
middle-man, you can. Say you want to have this service exposed on 10.0.0.8:4444.
For this, you execute the script on 10.0.0.8 as:

tunnel.py --tunnel 4444:10.0.0.16:7878

This will establish a tunnel between 10.0.0.8:4444 <--> 10.0.0.16:7878, and you can
communicate with 10.0.0.8:4444 to actually talk to 10.0.0.16:7878.
"""

epilogue = "Author: CaptainWoof. DM me @realCaptainWoof on Twitter for any bugs or suggestions."

parser = argparse.ArgumentParser(description=description, epilog=epilogue, allow_abbrev=False, add_help=False)
parser.add_argument('-t', '--timeout', action='store', help='Set global timeout',required=False,type=int,default=1)

verbose_quiet = parser.add_mutually_exclusive_group(required=False)
verbose_quiet.add_argument('-v', "--verbose", action='store_true', help="Start in verbose mode")
verbose_quiet.add_argument('-q', '--quiet', action='store_true', help="Start in quiet mode")

mutually_exclusive_params = parser.add_mutually_exclusive_group(required=True)
mutually_exclusive_params.add_argument('--help', "-h", action='store_true', help="Show detailed usage info")
mutually_exclusive_params.add_argument("--examples", action='store_true', help="Show usage examples")
mutually_exclusive_params.add_argument("--tunnel", action='store', help="Start the tunnelpy", type=str)

args = parser.parse_args()
verbose = args.verbose
quiet = args.quiet
colorAndFormat = ColorAndFormat()

if args.help:
    print(colorAndFormat.Greenbg2(banner) + '\n' + usage)
elif args.examples:
    print(colorAndFormat.Bluebg(banner) + '\n' + examples)
elif args.tunnel:
    try:
        if len(args.tunnel.split(':')) != 3:
            print("Wrong usage! Please use '--help' to see correct usage.")
            exit()

        mport = int(args.tunnel.split(':')[0])
        dhost = args.tunnel.split(':')[1]
        dport = int(args.tunnel.split(':')[2])

        tunnelpy = TunnelPy('', mport, dhost, dport, verbose, quiet,args.timeout)
        tunnelpy.start_listener()

    except Exception as e:
        print(colorAndFormat.Redbg(str(e)))
        exit()

