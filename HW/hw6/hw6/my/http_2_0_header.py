import ctypes

class http2Header(ctypes.BigEndianStructure):
    _fields_ = [
        ("length", ctypes.c_uint32),
        ("type", ctypes.c_uint8),
        ("flags", ctypes.c_uint8),
        ("streamId", ctypes.c_uint32),
    ]
    
    @staticmethod
    def getHeaderLength():
        return 9
    
    @staticmethod
    def getPacked(length, type, flags, streamId, data):
        header = http2Header()
        header.length = length
        header.type = type
        header.flags = flags
        header.streamId = streamId
        packet = bytes(header) + bytes(data, 'utf-8')

        return packet
    
    @staticmethod
    def getParsed(packet):
        header = http2Header.from_buffer_copy(packet)
        length, type, flags, streamId = header.length, header.type, header.flags, header.streamId
        data = packet[http2Header.getHeaderLength():].decode("utf-8")

        return length, type, flags, streamId, data
    
# length = 33
# type = 6
# flags = 15
# streamId = 1
# data = "shit"
# packet = http2Header.getPacked(length, type, flags, streamId, data)
# print(packet)

# length, type, flags, streamId, data = http2Header.getParsed(packet)
# print(length, type, flags, streamId, data)