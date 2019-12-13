import socket
import json
from client import get_directory_status

def changed_files(old_status, new_status):
    new_files = set(new_status.keys()).difference(set(old_status.keys()))
    common_files = set(new_status.keys()).intersection(set(old_status.keys()))

    changed = list(new_files)
    for f in common_files:
        if old_status[f] != new_status[f]:
            changed.append(f)

    return changed

def removed_files(old_status, new_status):
    return list(set(old_status.keys()).difference(set(new_status.keys())))

def run(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((socket.gethostname(), port))
        sock.listen(8)
        print("Listening on port {}".format(port))
        while True:
            conn, (client_host, client_port) = sock.accept()
            print("Connection from {} on port {}".format(client_host, client_port))
            new_status = conn.recv(2 ** 16) # TODO support larger status updates
            new_status = json.loads(new_status.decode("utf-8"))
            conn.sendall(json.dumps(changed_files(new_status, get_directory_status("."))).encode("utf-8"))
            conn.close() # TODO remove
