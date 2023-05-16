#! 請參照HW5筆記
#! 優先完成error control
# https://www.jianshu.com/p/ce6e0c472d3e
import socket
from quic_header import *

DATA = "Fuck you. ---- From server"


# UDP server doesn't need listen() and accept()
class QUICServer:
    def __init__(self):
        self.socket = None
        self.client_addr = None
    
    def listen(self, socket_addr: tuple[str, int]):
        """this method is to open the socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(socket_addr)
    
    def accept(self):
        """this method is to indicate that the client
        can connect to the server now"""
        _, self.client_addr = self.socket.recvfrom(1500)
    
    def send(self, stream_id: int, data: bytes):
        """call this method to send data, with non-reputation stream_id"""
        message = stream_id.to_bytes(4, byteorder='big') + data
        self.socket.sendto(message, self.client_addr)
    
    def recv(self) -> tuple[int, bytes]: # stream_id, data
        """receive a stream, with stream_id"""
        message, _ = self.socket.recvfrom(1500)
        stream_id = int.from_bytes(message[:4], byteorder='big')
        data = message[4:]
        return stream_id, data
    
    def close(self):
        """close the connection and the socket"""
        self.socket.close()


# server side
if __name__ == "__main__":
    print("Quic server running...")
    server = QUICServer()
    server.listen(("", 30000))
    server.accept()

    # while(True):
    for i in range(5):
        seq_num, ack_num, window_size = 10, 12, 14
        packet = QuicHeader.getPacked(seq_num, ack_num, window_size, DATA)
        server.send(1, packet)
        recv_id, packet = server.recv()
        seq_num, ack_num, window_size, data = QuicHeader.getParsed(packet)

        print(data)
        print(seq_num, ack_num, window_size)

    server.close() 