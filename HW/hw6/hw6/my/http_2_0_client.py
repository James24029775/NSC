# For HTTP/2

import os
import sys
import socket
import select
from collections import deque
import threading
import time
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from http_2_0_header import http2Header

CHUNK_SIZE = 4096

def prink(msg):
    print("\033[38;5;218m", msg, "\033[0m")
    
class Type:
    data = 0
    header = 1
    
class Flags:
    default = 0
    EOS = 1
    
class HTTPClient():
    def __init__(self) -> None:
        self.first = True
        self.client_socket = None
        self.streamIdCnt = 1
    
    def get(self, url, headers=None):
        # Send the request and return the response (Object)
        for i in range(len(url)):
            if url[i].isdigit():
                break
        url = url[i:].split("/")
        ip, port = url[0].split(":")[0], int(url[0].split(":")[1])
        path = ""
        for i in range(1, len(url)):
            path += url[i]
            if i != len(url)-1:
                path += "/"
                
        if path == "":
            path = "/"
            
        if self.first:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.client_socket.settimeout(5)
            self.first = False
        
        # Send request frame
        header = ":method: GET\r\n:path: " + path + "\r\n:version: HTTP/2.0\r\n:scheme: http\r\n"
        flags, type, streamId = Flags.EOS, Type.header, self.streamIdCnt
        self.streamIdCnt += 2
        frame = http2Header.getPacked(len(header), type, flags, streamId, header)
        self.client_socket.send(frame)
        # prink(frame)
        
        response = Response(socket=self.client_socket, stream_id=streamId)
        return response
    
    
class Response():
    b__ = b""
    
    def __init__(self, socket, stream_id, status = "Not yet") -> None:
        self.stream_id = stream_id
        self.headers = {}
        self.socket = socket
        
        self.status = status
        self.body = b""
        self.pool = deque()
        self.pool_lock = threading.Lock()
        self.b__lock = threading.Lock()

        self.contents = deque()
        self.complete = False
        self.rcvFlg = True
        self.cnt = 0
        
        
    def get_headers(self):
        inout = [self.socket]
        begin_time = time.time()
        while self.status == "Not yet":
            infds, outfds, errfds = select.select(inout, inout, [], 1)
            if time.time() - begin_time > 5:
                return None
            elif len(infds) != 0:
                self.status = "Received"
            
        dataFromBuffer = self.socket.recv(1024)
        length, type, flags, RcvStreamId, header = http2Header.getParsed(dataFromBuffer)

        header = header.split('\r\n')
        for i in range(1, len(header)):
            if header[i] == '':
                break
            if ':' in header[i]:
                key, value = header[i].split(':')[0].strip(), header[i].split(':')[1].strip()
                key = key.lower()
                self.headers[key] = value
        # prink(self.headers)
        return self.headers
    
    def get_full_body(self): # used for handling short body
        begin_time = time.time()
        while not self.complete:
            if time.time() - begin_time > 5:
                return None
            else:
                dataFromBuffer = self.socket.recv(1024)
                length, type, flags, RcvStreamId, data = http2Header.getParsed(dataFromBuffer)
                self.contents.append(data.encode())
                
                if flags == Flags.EOS:
                    self.complete = True
                
        if len(self.body) > 0:
            return self.body
            
        while len(self.contents) > 0:
            self.body += self.contents.popleft()
        
        # prink(self.body)
        return self.body # the full content of HTTP response body
    
    def get_stream_content(self): # used for handling long body
        try:
            if not self.complete:
                threading.Thread(target=self.receive_data).start()
                
            while not self.complete:
                if len(Response.b__) > 0:
                    length = int.from_bytes(Response.b__[:3], byteorder='big')
                    headFrame = Response.b__[:length + http2Header.getHeaderLength()]
                    length, type, flags, RcvStreamId, data = http2Header.getParsed(headFrame)
                    # print(length, type, flags, RcvStreamId)
                    
                    if str(RcvStreamId) == str(self.stream_id):
                        if flags == Flags.EOS:
                            self.complete = True
                        Response.b__ = Response.b__[length + http2Header.getHeaderLength():]
                        content = data.encode()
                        return content
                else:
                    return "".encode()
                    
            return None
        except:
            return "".encode()

    def receive_data(self):
        try:
            while not self.complete:
                with self.b__lock:
                    tb__ = self.socket.recv(CHUNK_SIZE + http2Header.getHeaderLength())
                    Response.b__ += tb__
                    length, type, flags, RcvStreamId, data = http2Header.getParsed(tb__)
        except:
            exit()
                
    def seperate(self, data):
        length, type, flags, RcvStreamId, others = http2Header.getParsed(data)
        index = http2Header.getHeaderLength() + length
        return data[:index], data[index:]