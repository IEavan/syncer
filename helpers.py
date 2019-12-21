import time
import hashlib
import json
import os
import socket

# File Operations and Helpers
def changed_files(old_status, new_status):
    """ Returns a list of files that are either new or have been modified. """
    new_files = set(new_status.keys()).difference(set(old_status.keys()))
    common_files = set(new_status.keys()).intersection(set(old_status.keys()))

    changed = list(new_files)
    for f in common_files:
        if old_status[f] != new_status[f]:
            changed.append(f)

    return changed

def removed_files(old_status, new_status):
    """ Returns a list of files that have been removed. """
    return list(set(old_status.keys()).difference(set(new_status.keys())))

def write_files(path, files_data):
    """ For each file in the files_data dictionary, it writes them to the path. """
    for filename, contents in files_data.items():
        full_path = os.path.join(path, filename)

        # Remove the file before writing new data to it
        if os.path.isfile(full_path):
            os.remove(full_path)

        print("Writing {}".format(full_path))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w+") as f:
            # Unescape newline characters
            f.write(contents.replace('@newline@', '\n'))

def file_chunks(filename, chunk_size=1024, readmode = "rb"):
    """ Generator returning the contents at a file one chunk at a time for easier handling. """
    with open(filename, readmode) as f:
        data = f.read(chunk_size)
        while data:
            yield data
            data = f.read(chunk_size)

def get_directory_status(path):
    """ Generate a dictionary of all the files in a directory specified by the path.
    
    The keys of the dictionary are the filenames and relative path and the values
    are the md5 hash. """
    
    directory = {}
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(path) for f in fn]
    for f in files:
        directory[f[f.find('/')+1:]] = hash_file(f)
    return directory

def hash_file(path):
    """ Compute the md5 hash of a file. """
    m = hashlib.md5()
    for chunk in file_chunks(path, chunk_size=2 ** 20): # read 1 MB at a time for large files
        m.update(chunk)
    return m.hexdigest()

# Socket Helpers
def send_status(sock, status):
    print("Sending directory status...")
    sock.sendall(json.dumps(status).encode("utf-8"))
    response = read_until_complete(sock)
    return response

def send_files(sock, requested_files):
    """ Sends a json of the requested files on the given socket. """
    sock.sendall(b'{')
    for i, f in enumerate(requested_files):
        print("Sending {}".format(f))
        sock.sendall(b'"' + f[f.find('/')+1:].encode("utf-8") + b'":"')
        for chunk in file_chunks(f):
            sock.sendall(chunk)
        sock.sendall(b'"')
        if i != len(requested_files) - 1:
            sock.sendall(b',')
    sock.sendall(b'}')

def read_until_complete(sock, chunk_size=1024, timeout=5):
    """ Reads from a socket until a full json object has been received.
    The function times out after a default of 5 seconds.
    
    Returns a dictionary if successful, None otherwise. """
    data = sock.recv(chunk_size)
    start_time = time.time()
    while True:
        try:
            new_status = data.decode("utf-8")

            # escape newlines with special character sequence 
            # due to them being illegal in json
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

