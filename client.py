import socket
import os
import hashlib
import json
import time

def read_until_complete(sock, chunk_size=1024, timeout=5):
    data = sock.recv(chunk_size)
    start_time = time.time()
    while True:
        try:
            new_status = data.decode("utf-8")
            new_status = json.loads(new_status)
            return new_status
        except json.decoder.JSONDecodeError:
            if time.time() - start_time > timeout:
                print("Timeout")
                break
            else:
                data += sock.recv(chunk_size)

def get_directory_status(path):
    directory = {}
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(path) for f in fn]
    for f in files:
        directory[f[f.find('/')+1:]] = hash_file(f)
    return directory

def hash_file(path):
    m = hashlib.md5()
    for chunk in file_chunks(path, chunk_size=2 ** 20): # read 1 MB at a time for large files
        m.update(chunk)
    return m.hexdigest()

def send_status(sock, status):
    print("Sending directory status...")
    sock.sendall(json.dumps(status).encode("utf-8"))
    response = read_until_complete(sock)
    return response

def send_files(sock, requested_files):
    sock.send(b'{')
    for i, f in enumerate(requested_files):
        print("Sending {}".format(f))
        sock.send(b'"' + f[f.find('/')+1:].encode("utf-8") + b'":"')
        for chunk in file_chunks(f):
            sock.sendall(chunk)
        sock.send(b'"')
        if i != len(requested_files) - 1:
            sock.send(b',')
    sock.send(b'}')

def file_chunks(filename, chunk_size=1024, readmode = "rb"):
    with open(filename, readmode) as f:
        data = f.read(chunk_size)
        while data:
            yield data
            data = f.read(chunk_size)
