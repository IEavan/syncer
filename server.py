import socket
import time
import json
import os
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

def read_until_complete(sock, chunk_size=1024, timeout=5):
    data = sock.recv(chunk_size)
    start_time = time.time()
    while True:
        try:
            new_status = data.decode("utf-8")
            new_status = new_status.replace('\n', '@newline@')
            new_status = json.loads(new_status)
            return new_status
        except json.decoder.JSONDecodeError:
            if time.time() - start_time > timeout:
                print("Timeout")
                print(data.decode("utf-8"))
                print(data.decode("utf-8").replace('\n', '@newline@'))
                break
            else:
                data += sock.recv(chunk_size)

def write_files(path, files_data):
    for filename, contents in files_data.items():
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            os.remove(full_path)
        print("Writing {}".format(full_path))
        with open(full_path, "w+") as f:
            f.write(contents.replace('@newline@', '\n'))

def run(port, path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((socket.gethostname(), port))
        sock.listen(8)
        print("Listening on port {}".format(port))
        while True:
            conn, (client_host, client_port) = sock.accept()
            print("Connection from {} on port {}".format(client_host, client_port))
            new_status = read_until_complete(conn) 
            conn.sendall(json.dumps(changed_files(get_directory_status(path), new_status)).encode("utf-8"))
            files_data = read_until_complete(conn)
            write_files(path, files_data)
