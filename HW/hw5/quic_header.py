import ctypes

class QuicHeader(ctypes.BigEndianStructure):
    _fields_ = [
        ("seq_num", ctypes.c_uint32),
        ("ack_num", ctypes.c_uint32),
        ("window_size", ctypes.c_uint16)
    ]

    @staticmethod
    def getHeaderLength():
        return 10
    
    @staticmethod
    def getPacked(seq_num, ack_num, window_size, data):
        header = QuicHeader()
        header.seq_num = seq_num
        header.ack_num = ack_num
        header.window_size = window_size
        packet = bytes(header) + bytes(data, 'utf-8')

        return packet
    
    @staticmethod
    def getParsed(packet):
        header = QuicHeader.from_buffer_copy(packet)
        seq_num, ack_num, window_size = header.seq_num, header.ack_num, header.window_size
        data = packet[QuicHeader.getHeaderLength():].decode("utf-8")

        return seq_num, ack_num, window_size, data

# seq_num = 1010
# ack_num = 5555
# window_size = 15
# data = "shit"
# packet = QuicHeader.getPacked(seq_num, ack_num, window_size, data)
# print(packet)

# seq_num, ack_num, window_size, data = QuicHeader.getParsed(packet)
# print(seq_num, ack_num, window_size, data)