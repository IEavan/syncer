import argparse
import socket
import os

from helpers import get_directory_status, send_status, send_files

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
    print("No address specified, using localhost {}".format(socket.gethostname()))
    args.addr = socket.gethostname()

if not (args.dest ^ args.source):
    print("Directory must be either the source or the destination")
    print("Exactly one of --source or --dest must be set")

if args.source:
    # Set up socket to send data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to {} on port {}".format(args.addr, args.port))
    try:
        sock.connect((args.addr, args.port))
    except ConnectionRefusedError:
        print("Could not Connect to server, check port {} and address {} are correct".format(args.port, args.addr))
        print("and that the server is running.")
        exit()
    dir_status = get_directory_status(args.dir)
    requested_files = send_status(sock, dir_status)
    print("Received response {}".format(requested_files))
    send_files(sock, [os.path.join(args.dir, f) for f in requested_files])
    sock.close()

if args.dest:
    import server
    server.run(args.port, args.dir)
