import socket
import signal
import os
import json
from helpers import read_until_complete, changed_files, get_directory_status, write_files, removed_files

def shutdown_server(sig, frame):
    print("\nShutting Down Server")
    server_socket.close()
    exit()
signal.signal(signal.SIGINT, shutdown_server)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
def run(port, path):
    server_socket.bind((socket.gethostname(), port))
    server_socket.listen(8)
    print("Listening on port {}".format(port))
    while True:
        conn, (client_host, client_port) = server_socket.accept()
        print("Connection from {} on port {}".format(client_host, client_port))
        new_status = read_until_complete(conn) 
        if new_status is None:
            print("Error reading status. Aborting Sync.")
            continue
        old_status = get_directory_status(path)
        for file_to_remove in removed_files(old_status, new_status):
            os.remove(os.path.join(path, file_to_remove))
            print("Removed {}".format(file_to_remove))
        conn.sendall(json.dumps(changed_files(old_status, new_status)).encode("utf-8"))
        files_data = read_until_complete(conn)
        if files_data is None:
            print("Error reading file data. Aborting Sync.")
            continue
        write_files(path, files_data)
