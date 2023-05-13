import socket
import random
import time
import os
import sys
import select
import threading
#! close實作錯誤！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！

def prink(msg):
    print("\033[38;5;218m" + msg + "\033[0m")


class HTTPServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.host = host
        self.port = port
        self.numOfTransmittedFiles = 0
        
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
            try:
                self.conn, self.addr = self.server_socket.accept()
                self.http_parser()
            except:
                exit()
            
    def http_parser(self):
        # Get the client request
        while True:
            request = self.conn.recv(1024).decode()
            prink(request)
            
            request = request.split(' ')[1]
            if request == '/':
                body = self.randomPickThreeFiles()
                head = self.makeHead(body)
                response = head + body
                
            elif 'static' in request:
                filename = request.split('/')[1]
                try:
                    with open(filename, 'r') as file:
                        body = file.read()
                except:
                    prink(filename, 'does not exist.')
                    raise ValueError
                
                head = self.makeHead(body)
                response = head + body
                self.numOfTransmittedFiles += 1
                
            # prink(response)
            prink(head)

            # Send HTTP response
            self.conn.sendall(response.encode())
            
            # After sleeping 1 second, close the connection
            if self.numOfTransmittedFiles == 3:
                time.sleep(1)
                self.conn.close()
                self.conn = ""
                prink('Connection ' + str(self.addr[0]) + ':' + str(self.addr[1]) + ' has closed.')
                self.numOfTransmittedFiles = 0
                break
        
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
        prink('HTTP/1.1 server has been closed.')
        exit()