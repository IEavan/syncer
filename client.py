import socket
import os
import hashlib
import json

def get_directory_status(path):
    directory = {}
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(path) for f in fn]
    for f in files:
        directory[f] = hash_file(f)

def hash_file(path):
    m = hashlib.md5()
    with open(path, "rb") as f:
        m.update(f.read())
    return m.hexdigest()

def send_status(sock, status):
    sock.sendall(json.dumps(status))
    response = sock.recv(1024)
    response = json.loads(response)
    return response

def send_files(sock, requested_files):
    for f in requested_files:
        send_file(sock, f)

def send_file(sock, filename):
    with open(filename, "rb") as f:
        data = f.read(1024)
        while data:
            sock.send(data)
            l.read(1024)

