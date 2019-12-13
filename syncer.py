import argparse
import socket
import client
import server

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("dir", help="The directory to synchronize to/from")
parser.add_argument("-s", "--source", help="Flag indicating that this is the source directory",
                    action="store_true")
parser.add_argument("-d", "--dest", help="Flag indicating that this is the destination directory",
                    action="store_true")
parser.add_argument("-a", "--addr", help="The address of the destination")
parser.add_argument("-p", "--port", help="The port of the destination",
                    type=int)

args = parser.parse_args()
if not args.addr:
    args.addr = socket.gethostname()

if not (args.dest ^ args.source):
    print("Directory must be either the source or the destination")
    print("Exactly one of --source or --dest must be set")

if args.source:
    # Set up socket to send data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to {} on port {}".format(args.addr, args.port))
    sock.connect((args.addr, args.port))
    dir_status = client.get_directory_status(".")
    response = client.send_status(sock, dir_status)
    print("Received response {}".format(response))
    sock.close()

if args.dest:
    server.run(args.port)
