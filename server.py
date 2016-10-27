#! venv/bin/python

import socket as soc
import random

def set_or_get(in_string):
    if in_string.startswith("/set?"):
        return ("set", in_string[5:])
    elif in_string.startswith("/get?"):
        return ("get", in_string[5:])
    else:
        return("none", "bad=notgood")

def parse_keyval(in_string):
    split = in_string.split("=")
    return (split[0], split[1])

def parse_request(request):
    # first line of entry is "GET /set?key=val HTTP/1.1"
    # we select the second entry
    get_header = request.split("\r\n")[0].split(" ")[1]
    command, keyval = set_or_get(get_header)
    key, val = parse_keyval(keyval)
    return command, key, val

def ok_request(msg):
    return "HTTP/1.1 200 OK\r\n\r\n%s" % msg

def bad_request(msg):
    return "HTTP/1.1 500 Internal Server Error\r\n\r\n%s" % msg

if __name__ == "__main__":
    database = {}

    serversocket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
    serversocket.bind(('localhost', 4000))
    serversocket.listen(5)

    while True:
        conn, addr = serversocket.accept()
        print "connection from %s" % str(addr)
        request = conn.recv(1028)
        try:
            command, key, val = parse_request(request)
        except:
            command = None
        if command == "set":
            database[key] = val
            conn.send(ok_request("database updated"))
        elif command == "get":
            resp_val = database[val]
            conn.send(ok_request(resp_val))
        else:
            conn.send(bad_request("parsing error"))
        conn.close()