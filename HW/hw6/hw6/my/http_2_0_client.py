# For HTTP/2

import sys
import socket
import select
import time
sys.path.append("/home/james/NSC/HW/hw6/hw6/my")
from http_2_0_header import http2Header

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
            self.first = False
        
        header = "GET " + path + " HTTP/2\r\n"
        flags, type, streamId = Flags.default, Type.header, 0
        frame = http2Header.getPacked(len(header), type, flags, streamId, header)
        prink(len(frame))
        prink(frame)
        self.client_socket.send(frame)
        
        response = Response(socket=self.client_socket, stream_id=streamId)
        return response
    
    
class Response():
    def __init__(self, socket, stream_id, status = "Not yet") -> None:
        self.stream_id = stream_id
        self.headers = {}
        self.socket = socket
        
        self.status = status
        self.body = b""

        self.contents = 'deque()'
        self.complete = False
        
        dataFromBuffer = self.socket.recv(1024).decode()
        print(dataFromBuffer)
        
    def get_headers(self):
        begin_time = time.time()
        while self.status == "Not yet":
            if time.time() - begin_time > 5:
                return None
        return self.headers
    
    def get_full_body(self): # used for handling short body
        begin_time = time.time()
        while not self.complete:
            if time.time() - begin_time > 5:
                return None
        if len(self.body) > 0:
            return self.body
        while len(self.contents) > 0:
            self.body += self.contents.popleft()
        return self.body # the full content of HTTP response body
    def get_stream_content(self): # used for handling long body
        begin_time = time.time()
        while len(self.contents) == 0: # contents is a buffer, busy waiting for new content
            if self.complete or time.time()-begin_time > 5: # if response is complete or timeout
                return None
        content = self.contents.popleft() # pop content from deque
        return content # the part content of the HTTP response body