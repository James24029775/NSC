import socket
import random
import time
import os
import sys
import select
import threading
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

class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.host = host
        self.port = port
        self.streamId = []
        self.numOfTransmittedFiles = 0
        self.TransmittedFileContents = []
        
    def run(self):
        # Create the server socket and start accepting connections
        # Use a thread to be the listenfd
        threading.Thread(target=self.start_server).start()
        
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        
        while True:
            self.conn, self.addr = self.server_socket.accept()
            self.http_parser()
            
    def http_parser(self):
        # Get the client request
        others = b""
        while True:
            if len(others) == 0:
                dataFromBuffer = self.conn.recv(1024)
                # prink(dataFromBuffer)
                others += dataFromBuffer
            frame, others = self.seperate(others)
            length, type, flags, RcvStreamId, request = http2Header.getParsed(frame)
            prink("Please wait few seconds for transmission...")
            print(request)
            
            request = request.split('\r\n')
            request_dict = {}
            for i in range(len(request)):
                if len(request[i]) == 0:
                    break
                key, value = request[i].split(':')[1].strip(), request[i].split(':')[2].strip()
                request_dict[key] = value
            request = request_dict['path']
                
            if request == '/':
                data = self.randomPickThreeFiles()
                header = self.makeHead(data)
                
            elif 'static' in request:
                filename = request.split('/')[1]
                try:
                    with open(filename, 'r') as file:
                        data = file.read()
                except:
                    prink(filename, 'does not exist.')
                    raise ValueError
                header = self.makeHead(data)
                
            # send header
            if request == '/':
                flags, type, sendStreamId = Flags.default, Type.header, RcvStreamId
                frame = http2Header.getPacked(len(header), type, flags, sendStreamId, header)
                self.conn.sendall(frame)
                
            # send data
            if 'static' in request:
                # send file_0x.txt
                self.TransmittedFileContents.append(data)
                self.streamId.append(RcvStreamId)
                # print(self.streamId)
                if len(self.TransmittedFileContents) == 3:
                    break
            else:
                # send index.html
                flags, type, sendStreamId = Flags.EOS, Type.data, RcvStreamId
                frame = http2Header.getPacked(len(data), type, flags, sendStreamId, data)
                self.conn.sendall(frame)
                
        startRecord = [0, 0, 0]
        while True:
            time.sleep(0.02)
            frame = b""
            for i in range(len(self.TransmittedFileContents)):
                # prink(self.streamId[i])
                start = startRecord[i]
                if startRecord[i] + CHUNK_SIZE >= len(self.TransmittedFileContents[i]):
                    end = len(self.TransmittedFileContents[i]) - 1
                    flags = Flags.EOS
                    self.numOfTransmittedFiles += 1
                else:
                    end = startRecord[i] + CHUNK_SIZE
                    startRecord[i] = end
                    flags = Flags.default
                    
                data = self.TransmittedFileContents[i][start:end]
                
                type, sendStreamId = Type.data, self.streamId[i]
                frame += http2Header.getPacked(len(data), type, flags, sendStreamId, data)
                # print(end, len(self.TransmittedFileContents[i]), flags, len(frame))
            
            self.conn.sendall(frame)
            if self.numOfTransmittedFiles == 3:
                time.sleep(1)
                self.conn.close()
                self.conn = ""
                prink('Connection ' + str(self.addr[0]) + ':' + str(self.addr[1]) + ' has closed.')
                self.numOfTransmittedFiles = 0
                break
            
    def seperate(self, data):
        length, type, flags, RcvStreamId, others = http2Header.getParsed(data)
        index = http2Header.getHeaderLength() + length
        return data[:index], data[index:]
        
    def randomPickThreeFiles(self):
        numbers = random.sample(range(0, 10), 3)
        body = f'''<html>
            <header>
            </header>
            <body>
                <a href="/static/file_0{numbers[0]}.txt">file_0{numbers[0]}.txt</a>
                <br/>
                <a href="/static/file_0{numbers[1]}.txt">file_0{numbers[1]}.txt</a>
                <br/>
                <a href="/static/file_0{numbers[2]}.txt">file_0{numbers[2]}.txt</a>
            </body>
        </html>
        '''
        
        return body
        
    def makeHead(self, body):
        contenLength = len(body)
        head = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length:{contenLength}\r\n\r\n'
        return head
    
    def set_static(self, path):
        # Set the static directory so that when the client sends a GET request to the resource "/static/<file_name>", the file located in the static directory is sent back in the response.
        self.path = path
        os.chdir(self.path)
    
    def close(self):
        # Close the server socket.
        self.server_socket.close()
        prink('HTTP/2.0 server has been closed.')
        exit()