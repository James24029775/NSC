#! 請參照HW5筆記
#! 優先完成error control
# https://www.jianshu.com/p/ce6e0c472d3e
import socket
from quic_header import *

DATA = "Eat my shit. ---- From client"


class QUICClient:
    def __init__(self):
        self.socket = None
        self.socket_addr = None
    
    def connect(self, socket_addr: tuple[str, int]):
        """connect to the specific server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_addr = socket_addr
        self.send(2, b"Hello Server!")

    
    def send(self, stream_id: int, data: bytes):
        """call this method to send data, with non-reputation stream_id"""
        message = stream_id.to_bytes(4, byteorder='big') + data
        self.socket.sendto(message, self.socket_addr)
    
    def recv(self) -> tuple[int, bytes]: # stream_id, data
        """receive a stream, with stream_id"""
        message = self.socket.recv(1500)
        stream_id = int.from_bytes(message[:4], byteorder='big')
        data = message[4:]
        return stream_id, data
    
    def close(self):
        """close the connection and the socket"""
        self.socket.close()


# client side
if __name__ == "__main__":
    print("Quic client running...")
    client = QUICClient()
    client.connect(("127.0.0.1", 30000))

    for i in range(5):
        recv_id, packet = client.recv()
        seq_num, ack_num, window_size, data = QuicHeader.getParsed(packet)
        print(data)
        print(seq_num, ack_num, window_size)

        seq_num, ack_num, window_size = 100, 120, 140
        packet = QuicHeader.getPacked(seq_num, ack_num, window_size, DATA)
        client.send(2, packet)

    client.close()