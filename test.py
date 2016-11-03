#! venv/bin/python

import socket as soc
import threading

def get(n):
    for i in range(4):
        socket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
        socket.connect(('localhost', 4000))
        socket.send("GET /get?key=foo HTTP/1.1")
        resp = socket.recv(1024)
        print "response from get %d%d: %s" % (n, i, resp)
        socket.close()

def set(n):
    for i in range(4):
        socket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
        socket.connect(('localhost', 4000))
        socket.send("GET /set?foo=%d%d HTTP/1.1" % (n,i))
        resp = socket.recv(1024)
        print "response from set %d%d: %s" % (n, i, resp)
        socket.close()

def main(i):
    getthreads = [threading.Thread(target=get, args=(n,)) 
                                        for n in range(i)]
    setthreads = [threading.Thread(target=set, args=(n,)) 
                                        for n in range(i)]
    for t in range(i):
        getthreads[t].start()
        setthreads[t].start()

if __name__ == "__main__":
    main(3)

