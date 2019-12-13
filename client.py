import socket
import os
import hashlib
import json

def get_directory_status(path):
    directory = {}
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(path) for f in fn]
    for f in files:
        directory[f] = hash_file(f)
    return directory

def hash_file(path):
    m = hashlib.md5()
    for chunk in file_chunks(path, chunk_size=2 ** 20): # read 1 MB at a time for large files
        m.update(chunk)
    return m.hexdigest()

def send_status(sock, status):
    print("Sending directory status...")
    sock.sendall(json.dumps(status).encode("utf-8"))
    response = sock.recv(1024)
    response = json.loads(response.decode("utf-8"))
    return response

def send_files(sock, requested_files):
    for f in requested_files:
        send_file(sock, f)

def send_file(sock, filename):
    for chunk in file_chunks(filename):
        sock.sendall(chunk)

def file_chunks(filename, chunk_size=1024, readmode = "rb"):
    with open(filename, readmode) as f:
        data = f.read(chunk_size)
        while data:
            yield data
            data = f.read(chunk_size)
