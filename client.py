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
