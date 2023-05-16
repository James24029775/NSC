# For HTTP/1.X

import sys
import socket
import select

def prink(msg):
    print("\033[38;5;218m", msg, "\033[0m")

class HTTPClient():
    def __init__(self) -> None:
        self.first = True
        self.client_socket = None
    
    def get(self, url, headers=None, stream=False):
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
        
        # print(ip, port, path)
        if self.first:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.first = False
        
        request = "GET " + path + " HTTP/1.1\r\n"
        self.client_socket.send(request.encode())
        
        response = Response(self.client_socket, stream)
        # If stream=True, the response should be returned immediately after the full headers have been received.
        return response
    
    
class Response():
    def __init__(self, socket, stream) -> None:
        self.socket = socket
        self.stream = stream

        # fieleds
        self.version = "" # e.g., "HTTP/1.1"
        self.status = ""  # e.g., "200 OK"
        self.headers = {} # e.g., {content-type: application/json}
        self.body = b""  # e.g. "{'id': '123', 'key':'456'}"
        self.body_length = 0
        self.complete = False
        self.__reamin_bytes = b""
        
        dataFromBuffer = self.socket.recv(1024).decode()
        dataFromBuffer = dataFromBuffer.split('\r\n')
        for i in range(1, len(dataFromBuffer)):
            if dataFromBuffer[i] == '':
                break
            if ':' in dataFromBuffer[i]:
                key, value = dataFromBuffer[i].split(':')[0].strip(), dataFromBuffer[i].split(':')[1].strip()
                key = key.lower()
                self.headers[key] = value
        # prink(self.headers)
        self.body = dataFromBuffer[i+1].encode()
        self.body_length += len(self.body)
        
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!等待http_2_0_client_demo.py完成後再移植過來
    def get_full_body(self): # used for handling short body
        if self.stream or not self.complete:
            return None
        return self.body # the full content of HTTP response body
    
    def get_stream_content(self): # used for handling long body
        if not self.stream or self.complete:
            return None
        # 若body非空就先回傳
        if self.body != b"":
            content = self.body
            self.body = b""
            return content
        # 否則繼續從buffer拿資料
        content = self.get_remain_body() # recv remaining body data from socket
        return content # the part content of the HTTP response body
    
    def get_remain_body(self):
        inout = [self.socket]
        infds, outfds, errfds = select.select(inout, inout, [], 5)
        if len(infds) != 0:
            dataFromBuffer = self.socket.recv(1024)
            self.body_length += len(dataFromBuffer)
            # prink(str(self.body_length) + '/' + self.headers['content-length'])
            if self.body_length == self.headers['content-length']:
                self.complete = True
            return dataFromBuffer
        else:
            return None