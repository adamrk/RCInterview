#! venv/bin/python

"""
Task: Database Server

Before your interview, write a program that runs a server that is 
accessible on http://localhost:4000/. When your server receives a 
request on http://localhost:4000/set?somekey=somevalue it should 
store the passed key and value in memory. When it receives a 
request on http://localhost:4000/get?key=somekey it should return 
the value stored at somekey.

During your interview, you will pair on saving the data to a file. 
You can start with simply appending each write to the file, and 
work on making it more efficient if you have time.
"""

import socket as soc
import cPickle
import threading

def set_or_get(in_string):
    # reads http path from header
    # returns weather command is get or set and the k/v pair
    if in_string.startswith("/set?"):
        return ("set", in_string[5:])
    elif in_string.startswith("/get?"):
        return ("get", in_string[5:])
    else:
        return(None, None)

def parse_keyval(in_string):
    # parses "key=value" into tuple ("key", "value")
    split = in_string.split("=")
    return (split[0], split[1])

def parse_request(request):
    # first line of entry is "GET /set?key=val HTTP/1.1"
    # we select the second entry: "/set?key=val"
    get_header = request.split("\r\n")[0].split(" ")[1]
    command, keyval = set_or_get(get_header)
    key, val = parse_keyval(keyval)
    return command, key, val

def ok_request(msg):
    return "HTTP/1.1 200 OK\r\n\r\n%s\r\n" % msg

def bad_request(msg):
    return "HTTP/1.1 500 Internal Server Error\r\n\r\n%s\r\n" % msg

def handle_conn(conn, addr, database, db_lock):
    request = conn.recv(1024)
    print "request received:\n%s" % request.split("\r\n")[0]
    try:
        command, key, val = parse_request(request)
        # this will throw error if request doens't fit
        # '/set?key=val' or '/get?key=val'
    except:
        command = None
    if command == "set":
        with db_lock:
            database[key] = val
            file = open('db', 'w')
            cPickle.dump(database, file)
            file.close()
        conn.send(ok_request("database updated"))
    elif command == "get":
        try:
            resp_val = database[val]
            conn.send(ok_request(resp_val))
        except KeyError:
            conn.send(bad_request("key not present"))
    else:
        conn.send(bad_request("parsing error"))
    conn.close()

def run_server():
    dbfile = open('db', 'a+')
    try:
        database = cPickle.load(dbfile) #just save key/values in a dict
    except EOFError:
        database = {}
    dbfile.close()
    db_lock = threading.RLock()

    # socket to listen for connections
    serversocket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
    serversocket.bind(('localhost', 4000))
    serversocket.listen(5)

    while True:
        conn, addr = serversocket.accept()
        print "connection from %s" % str(addr)
        thread = threading.Thread(
            target=handle_conn,
            args=(conn, addr, database, db_lock))
        thread.start()
        

if __name__ == "__main__":
    run_server()