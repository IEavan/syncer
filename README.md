# Syncer
A tool for syncronizing two directories over a network written in python.

# Usage
Python 3 is required, syncer is not compatible with Python 2 due to changes to the socket library.  
    syncer.py [-h] [-s] [-d] [-a ADDR] [-p PORT] dir

    positional arguments:  
      dir                   The directory to synchronize to/from  

    optional arguments:  
      -h, --help            show this help message and exit  
      -s, --source          Flag indicating that this is the source directory  
      -d, --dest            Flag indicating that this is the destination directory  
      -a ADDR, --addr ADDR  The address of the destination  
      -p PORT, --port PORT  The port of the destination  

## Example Usage
On Server: python3 syncer.py --dest --port 45454 test\_dest  
On Client: python3 syncer.py --source --port 45454 test\_source  

It's important that these commands are run in this order, as the client expects the server to be running.
